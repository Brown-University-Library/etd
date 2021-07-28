import datetime
import json
import os
import requests
from django.conf import settings
from .models import Thesis, Degree
from .mods_mapper import ModsMapper


class IngestException(Exception):
    pass


class ThesisIngester:

    def __init__(self, thesis):
        if not thesis.ready_to_ingest():
            raise Exception(f'thesis {thesis.id} not ready for ingestion')
        self.thesis = thesis

    @property
    def embargo_end_year(self):
        return self.thesis.candidate.embargo_end_year

    def get_rights_param(self):
        rights_params = {'owner_id': settings.OWNER_ID}
        if self.thesis.candidate.private_access_end_date:
            pass
        elif self.embargo_end_year:
            rights_params['additional_rights'] = '%s#discover,display+%s#discover' % (settings.EMBARGOED_DISPLAY_IDENTITY, settings.PUBLIC_DISPLAY_IDENTITY)
        else:
            rights_params['additional_rights'] = '%s#discover,display' % settings.PUBLIC_DISPLAY_IDENTITY
        return json.dumps({'parameters': rights_params})

    def get_ir_param(self):
        ir_params = {'ir_collection_id': self.thesis.candidate.department.bdr_collection_id,
                     'depositor_name': 'ETD application'}
        return json.dumps({'parameters': ir_params})

    def get_mods_param(self):
        MODS_XML = ModsMapper(self.thesis).get_mods().serialize().decode('utf8')
        return json.dumps({'xml_data': MODS_XML})

    def get_rels_param(self):
        rels = {}
        if self.thesis.candidate.degree.degree_type == Degree.TYPES.masters:
            rels['type'] = 'http://purl.org/spar/fabio/MastersThesis'
        else:
            rels['type'] = 'http://purl.org/spar/fabio/DoctoralThesis'
        rels['resource_type'] = 'dissertations'
        if self.embargo_end_year:
            rels['embargo_end'] = '%s-12-31T23:00:01Z' % self.embargo_end_year
        return json.dumps(rels)


    def get_content_param(self):
        return json.dumps([{'file_name': '%s' % self.thesis.current_file_name}])

    def get_ingest_params(self):
        params = {}
        params['rights'] = self.get_rights_param()
        params['ir'] = self.get_ir_param()
        params['mods'] = self.get_mods_param()
        rels = self.get_rels_param()
        if rels:
            params['rels'] = rels
        params['content_streams'] = self.get_content_param()
        params['identity'] = settings.POST_IDENTITY
        params['authorization_code'] = settings.AUTHORIZATION_CODE
        return params

    def post_to_api(self, params):
        with open(os.path.join(settings.MEDIA_ROOT, self.thesis.current_file_name), 'rb') as f:
            try:
                r = requests.post(settings.API_URL, data=params, files={self.thesis.current_file_name: f})
            except Exception as e:
                raise IngestException('%s' % e)
        if r.ok:
            return r.json()['pid']
        else:
            raise IngestException('%s - %s' % (r.status_code, r.content))

    def ingest(self):
        params = self.get_ingest_params()
        try:
            pid = self.post_to_api(params)
            self.thesis.mark_ingested(pid)
            return pid
        except IngestException as ie:
            self.thesis.mark_ingest_error()
            raise


def find_theses_to_ingest(dt=None):
    if not dt:
        date_ready = datetime.date.today()
    elif isinstance(dt, str):
        date_ready = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
    elif isinstance(dt, datetime.date):
        date_ready = dt
    else:
        raise Exception(f'invalid date: {dt}')
    accepted_theses = Thesis.objects.filter(status=Thesis.STATUS_CHOICES.accepted).order_by('title')
    #need ready_to_ingest check, because a thesis being "accepted" doesn't mean it's ready to ingest
    return [th for th in accepted_theses if th.ready_to_ingest(date_ready)]


def ingest_batch_of_theses(dt=None):
    theses_batch = find_theses_to_ingest(dt)
    print('Found %s theses/dissertations to ingest.' % len(theses_batch))
    for thesis in theses_batch:
        print('  %s - %s' % (thesis.candidate, thesis))
        ti = ThesisIngester(thesis)
        ti.ingest()
