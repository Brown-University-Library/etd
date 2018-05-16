from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from etd_app.models import Thesis
from tests.test_views import CandidateCreator
from tests.test_models import LAST_NAME


THESIS_TITLE = '“iñtërnâtiônàlĭzætiøn”'


class TestThesisAdmin(CandidateCreator, TestCase):

    def _setup_user(self):
        u = User.objects.create(username='staff@brown.edu')
        u.is_staff = True
        u.is_superuser = True
        u.save()

    def _setup_thesis(self):
        self._create_candidate()
        thesis = self.candidate.thesis
        thesis.title = THESIS_TITLE
        thesis.save()

    def test_changelist(self):
        self._setup_user()
        self._setup_thesis()
        url = reverse('admin:etd_app_thesis_changelist')
        r = self.client.get(url, follow=True, **{
                        'Shibboleth-eppn': 'staff@brown.edu',
                        'REMOTE_USER': 'staff@brown.edu'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, THESIS_TITLE)

    def test_changelist_search(self):
        self._setup_user()
        self._setup_thesis()
        self._create_second_candidate()
        second_title = 'Second candidate title'
        self.candidate2.thesis.title = second_title
        self.candidate2.thesis.save()
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

