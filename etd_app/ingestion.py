import json
import os
import requests
from django.conf import settings
from .models import Thesis
from .mods_mapper import ModsMapper


class IngestException(Exception):
    pass


class ThesisIngester(object):

    def __init__(self, thesis):
        if not (thesis.ready_to_ingest() and thesis.candidate.gradschool_checklist.complete()):
            raise Exception('thesis not ready for ingestion')
        self.thesis = thesis

    @property
    def embargo_end_year(self):
        return self.thesis.candidate.embargo_end_year

    @property
    def api_url(self):
        return settings.API_URL

    def get_rights_param(self):
        rights_params = {'owner_id': settings.OWNER_ID}
        if self.embargo_end_year:
            rights_params['additional_rights'] = '%s#discover,display+%s#discover' % (settings.EMBARGOED_DISPLAY_IDENTITY, settings.PUBLIC_DISPLAY_IDENTITY)
        else:
            rights_params['additional_rights'] = '%s#discover,display' % settings.PUBLIC_DISPLAY_IDENTITY
        return json.dumps({'parameters': rights_params})

    def get_ir_param(self):
        ir_params = {'ir_collection_id': self.thesis.candidate.department.bdr_collection_id,
                     'depositor_name': 'ETD application'}
        return json.dumps({'parameters': ir_params})

    def get_mods_param(self):
        MODS_XML = ModsMapper(self.thesis).get_mods().serialize()
        return json.dumps({'xml_data': MODS_XML})

    def get_rels_param(self):
        if self.embargo_end_year:
            return json.dumps({'embargo_end': '%s-06-01T00:00:01Z' % self.embargo_end_year})

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
                r = requests.post(self.api_url, data=params, files={self.thesis.current_file_name: f})
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
