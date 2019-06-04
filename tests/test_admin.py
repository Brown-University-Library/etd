from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from etd_app.models import Thesis
from tests.test_views import CandidateCreator
from tests.test_models import LAST_NAME, complete_gradschool_checklist, CURRENT_YEAR


THESIS_TITLE = '“iñtërnâtiônàlĭzætiøn”'


def setup_user():
    u = User.objects.create(username='staff@brown.edu')
    u.is_staff = True
    u.is_superuser = True
    u.save()


def setup_thesis(testcase_instance, status=None):
    testcase_instance._create_candidate()
    thesis = testcase_instance.candidate.thesis
    thesis.title = THESIS_TITLE
    if status:
        thesis.status = status
    thesis.save()


class TestThesisAdmin(CandidateCreator, TestCase):

    def test_changelist(self):
        setup_user()
        setup_thesis(self)
        url = reverse('admin:etd_app_thesis_changelist')
        r = self.client.get(url, follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, THESIS_TITLE)

    def test_open_for_reupload_action(self):
        setup_user()
        setup_thesis(self, status=Thesis.STATUS_CHOICES.accepted)
        thesis = Thesis.objects.all()[0]
        self.assertEqual(thesis.status, Thesis.STATUS_CHOICES.accepted)
        url = reverse('admin:etd_app_thesis_changelist')
        post_data = {'_selected_action': [str(self.candidate.thesis.id)], 'action': 'open_for_reupload'}
        r = self.client.post(url, post_data, follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        thesis = Thesis.objects.all()[0]
        self.assertEqual(thesis.status, Thesis.STATUS_CHOICES.not_submitted)

    def test_changelist_search(self):
        setup_user()
        setup_thesis(self)
        second_title = 'Second candidate title'
        candidate2 = self._create_additional_candidate(thesis_title=second_title)
        url = reverse('admin:etd_app_thesis_changelist')
        title_element = f'<td class="field-title">{THESIS_TITLE}</td>'
        second_title_element = '<td class="field-title">Second candidate title</td>'
        #test last name
        r = self.client.get(f'{url}?q={LAST_NAME}', follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertContains(r, title_element)
        self.assertNotContains(r, second_title_element)
        #test first name
        r = self.client.get(f'{url}?q=Mary', follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertContains(r, second_title_element)
        self.assertNotContains(r, title_element)
        #test title
        r = self.client.get(f'{url}?q={THESIS_TITLE}', follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertContains(r, title_element)
        self.assertNotContains(r, second_title_element)

    def test_status_filter(self):
        setup_user()
        setup_thesis(self, status=Thesis.STATUS_CHOICES.accepted)
        complete_gradschool_checklist(self.candidate)
        second_title = 'another title'
        candidate2 = self._create_additional_candidate(thesis_title=second_title)
        url = reverse('admin:etd_app_thesis_changelist')
        r = self.client.get(f'{url}?status__exact=accepted', follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertContains(r, THESIS_TITLE)
        self.assertNotContains(r, second_title)

    def test_ready_to_ingest_filter(self):
        setup_user()
        setup_thesis(self, status=Thesis.STATUS_CHOICES.accepted)
        complete_gradschool_checklist(self.candidate)
        second_title = 'another title'
        candidate2 = self._create_additional_candidate(thesis_title=second_title)
        thesis2 = candidate2.thesis
        thesis2.status = Thesis.STATUS_CHOICES.accepted
        thesis2.save()
        url = reverse('admin:etd_app_thesis_changelist')
        r = self.client.get(f'{url}?ready_to_ingest=yes', follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertContains(r, THESIS_TITLE)
        self.assertNotContains(r, second_title)

    def test_ready_to_ingest_filter_large_list(self):
        setup_user()
        setup_thesis(self, status=Thesis.STATUS_CHOICES.accepted)
        complete_gradschool_checklist(self.candidate)
        for i in range(500):
            person = self._create_person(netid=f'user{i}@school.edu', email=f'user{i}@school.edu')
            candidate = self._create_additional_candidate(person=person)
            candidate.thesis.status = Thesis.STATUS_CHOICES.accepted
            candidate.thesis.save()
            complete_gradschool_checklist(candidate)
        url = reverse('admin:etd_app_thesis_changelist')
        r = self.client.get(f'{url}?ready_to_ingest=yes', follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertContains(r, '501 Theses')



class TestCandidateAdmin(CandidateCreator, TestCase):

    def test_display_candidate(self):
        setup_user()
        setup_thesis(self)
        url = reverse('admin:etd_app_candidate_change', args=(self.candidate.id,))
        r = self.client.get(url, follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id_private_access_end_date')

