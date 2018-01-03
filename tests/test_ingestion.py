import json
from django.test import TestCase
from django.utils import timezone

from etd_app.mods_mapper import ModsMapper
from etd_app.ingestion import ThesisIngester, find_theses_to_ingest
from etd_app.models import Keyword, Degree, Person, Candidate, Thesis
from tests.test_models import LAST_NAME, FIRST_NAME, CURRENT_YEAR, add_metadata_to_thesis
from tests.test_views import CandidateCreator


class TestModsMapper(TestCase, CandidateCreator):

    def test_mapping(self):
        today = timezone.now().date()
        self._create_candidate()
        self.candidate.person.middle = 'Middle'
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.committee_members.add(self.committee_member2)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.thesis.keywords.add(Keyword.objects.create(text='kw2', authority='fast', authority_uri='http://fast.com',
                                           value_uri='http://fast.com/kw2'))
        self.candidate.thesis.num_prelim_pages = 'x'
        self.candidate.thesis.num_body_pages = '125'
        self.candidate.thesis.save()
        mapper = ModsMapper(self.candidate.thesis)
        mods = mapper.get_mods()
        self.assertEqual(mods.title, 'test')
        creators = [n for n in mods.names if (n.type == 'personal') and (n.roles[0].text == 'creator') and (n.roles[0].type == 'text')]
        self.assertEqual(creators[0].name_parts[0].text, '%s, %s Middle' % (LAST_NAME, FIRST_NAME))
        self.assertEqual(mods.origin_info.copyright[0].date, str(CURRENT_YEAR))
        self.assertEqual(mods.physical_description.extent, 'x, 125 p.')
        self.assertEqual(mods.physical_description.digital_origin, 'born digital')
        self.assertEqual(mods.notes[0].type, 'thesis')
        self.assertEqual(mods.notes[0].text, 'Thesis (Ph.D.)--Brown University, %s' % CURRENT_YEAR)
        self.assertEqual(mods.resource_type, 'text')
        self.assertEqual(mods.genres[0].text, 'theses')
        self.assertEqual(mods.genres[0].authority, 'aat')
        self.assertEqual(mods.abstract.text, 'test abstract')
        readers = [n for n in mods.names if (n.type == 'personal') and (n.roles[0].text == 'Reader') and (n.roles[0].type == 'text')]
        self.assertEqual(readers[0].name_parts[0].text, 'Smith')
        advisors = [n for n in mods.names if (n.type == 'personal') and (n.roles[0].text == 'Advisor') and (n.roles[0].type == 'text')]
        self.assertEqual(advisors[0].name_parts[0].text, 'Smith')
        sponsors = [n for n in mods.names if (n.type == 'corporate') and (n.roles[0].text == 'sponsor') and (n.roles[0].type == 'text')]
        self.assertEqual(sponsors[0].name_parts[0].text, 'Brown University. Engineering')
        self.assertEqual(mods.subjects[0].topic, 'keyword')
        self.assertEqual(mods.subjects[1].topic, 'kw2')
        self.assertEqual(mods.subjects[1].authority, 'fast')
        self.assertEqual(mods.subjects[1].authority_uri, 'http://fast.com')
        self.assertEqual(mods.subjects[1].value_uri, 'http://fast.com/kw2')
        self.assertEqual(mods.record_info_list[0].record_content_source.text, 'RPB')
        self.assertEqual(mods.record_info_list[0].record_content_source.authority, 'marcorg')
        self.assertEqual(mods.record_info_list[0].record_creation_date.encoding, 'iso8601')
        self.assertEqual(mods.record_info_list[0].record_creation_date.date, today.strftime('%Y%m%d'))
        #thesis language automatically defaults to English
        self.assertEqual(mods.languages[0].terms[0].text, 'English')
        self.assertEqual(mods.languages[0].terms[0].authority, 'iso639-2b')
        self.assertTrue(mods.is_valid())


class TestIngestion(TestCase, CandidateCreator):

    def _complete_thesis(self, thesis=None):
        if not thesis:
            thesis = self.candidate.thesis
        thesis.status = 'accepted'
        thesis.save()
        candidate = thesis.candidate
        now = timezone.now()
        candidate.gradschool_checklist.dissertation_fee = now
        candidate.gradschool_checklist.bursar_receipt = now
        candidate.gradschool_checklist.gradschool_exit_survey = now
        candidate.gradschool_checklist.earned_docs_survey = now
        candidate.gradschool_checklist.pages_submitted_to_gradschool = now
        candidate.gradschool_checklist.save()

    def test_find_theses_to_ingest(self):
        self._create_candidate()
        self.assertEqual(len(find_theses_to_ingest()), 0)
        self.candidate.thesis.status = Thesis.STATUS_CHOICES.accepted
        self.candidate.thesis.save()
        self.assertEqual(len(find_theses_to_ingest()), 0)
        self._complete_thesis()
        self.assertEqual(len(find_theses_to_ingest()), 1)
        person2 = Person.objects.create(netid='p2@brown.edu', last_name='a', first_name='b',
                email='ab@brown.edu')
        candidate2 = Candidate.objects.create(person=person2, year=(CURRENT_YEAR+1), department=self.dept, degree=self.degree)
        self._complete_thesis(candidate2.thesis)
        self.assertEqual(len(find_theses_to_ingest()), 1)

    def test_status(self):
        self._create_candidate()
        with self.assertRaises(Exception) as cm:
            ThesisIngester(self.candidate.thesis)
        #make sure we can create the ThesisIngester if we complete the thesis/checklist
        self._complete_thesis()
        ti = ThesisIngester(self.candidate.thesis)

    def test_params(self):
        #first check doctoral thesis
        self._create_candidate()
        self._complete_thesis()
        ti = ThesisIngester(self.candidate.thesis)
        params = ti.get_ingest_params()
        rels = json.loads(params['rels'])
        self.assertTrue('embargo_end' not in rels)
        self.assertEqual(rels['type'], 'http://purl.org/spar/fabio/DoctoralThesis')
        #and now check masters
        self.candidate.degree.degree_type = Degree.TYPES.masters
        ti = ThesisIngester(self.candidate.thesis)
        params = ti.get_ingest_params()
        rels = json.loads(params['rels'])
        self.assertEqual(rels['type'], 'http://purl.org/spar/fabio/MastersThesis')

    def test_params_embargo(self):
        self._create_candidate()
        self.candidate.embargo_end_year = CURRENT_YEAR + 2
        self.candidate.save()
        self._complete_thesis()
        ti = ThesisIngester(self.candidate.thesis)
        params = ti.get_ingest_params()
        rels_param = json.loads(params['rels'])
        self.assertEqual(rels_param['embargo_end'], '%s-06-01T00:00:01Z' % (CURRENT_YEAR+2))

