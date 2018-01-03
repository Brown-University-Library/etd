import json
import os
from django.contrib.auth.models import User, Permission
from django.core.files import File
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpRequest
from django.test import SimpleTestCase, TestCase
from django.test.client import Client, MULTIPART_CONTENT, BOUNDARY
from django.utils import timezone
from django.utils.encoding import force_bytes
import responses
from tests import responses_data
from tests.test_models import TEST_PDF_FILENAME, LAST_NAME, FIRST_NAME, CURRENT_YEAR, add_file_to_thesis, add_metadata_to_thesis
from etd_app.models import Person, Candidate, CommitteeMember, Department, Degree, Thesis, Keyword
from etd_app.views import get_shib_info_from_request, _get_previously_used, _get_fast_results, candidate_metadata
from etd_app.widgets import ID_VAL_SEPARATOR


def get_auth_client():
    user = User.objects.create_user('tjones@brown.edu', 'pw')
    auth_client = Client()
    auth_client.force_login(user)
    return auth_client


def get_staff_client():
    user = User.objects.create_user('staff@brown.edu', 'pw')
    change_candidate_perm = Permission.objects.get(codename='change_candidate')
    user.user_permissions.add(change_candidate_perm)
    staff_client = Client()
    staff_client.force_login(user)
    return staff_client


class TestStaticViews(SimpleTestCase):

    def test_redirect(self):
        response = self.client.get('/index.php')
        self.assertRedirects(response, reverse('home'), status_code=301)

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<title>Electronic Theses &amp; Dissertations at Brown University')
        self.assertContains(response, 'Ph.D. candidates at Brown must file their dissertations electronically.')
        self.assertContains(response, 'Deposit My Dissertation')
        self.assertContains(response, 'Admin')

    def test_overview(self):
        response = self.client.get(reverse('overview'))
        self.assertContains(response, 'Submission Overview')

    def test_faq(self):
        response = self.client.get(reverse('faq'))
        self.assertContains(response, 'Where are Brown’s ETDs available?')

    def test_copyright(self):
        response = self.client.get(reverse('copyright'))
        self.assertContains(response, 'You own the copyright to your dissertation')


class CandidateCreator(object):
    '''mixin object for creating PhD candidates'''

    @property
    def cur_dir(self):
        return os.path.dirname(os.path.abspath(__file__))

    def _create_candidate(self, degree_type=Degree.TYPES.doctorate):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D.', name='Doctor', degree_type=degree_type)
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, first_name=FIRST_NAME,
                email='tom_jones@brown.edu')
        cm_person = Person.objects.create(last_name='Smith')
        self.committee_member = CommitteeMember.objects.create(person=cm_person, department=self.dept)
        self.committee_member2 = CommitteeMember.objects.create(person=cm_person, department=self.dept, role='advisor')
        self.candidate = Candidate.objects.create(person=self.person, year=CURRENT_YEAR, department=self.dept, degree=self.degree)


class TestRegister(TestCase, CandidateCreator):

    def setUp(self):
        #set an incorrect netid here, to make sure it's read from the username instead of
        #   the passed in value - we don't want someone to be able to register for a different user.
        self.person_data = {'netid': 'wrongid@brown.edu', 'orcid': '1234567890',
                'last_name': LAST_NAME, 'first_name': FIRST_NAME,
                'email': 'tomjones@brown.edu', 'phone': '401-123-1234'}

    def test_register_auth(self):
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, '%s?next=/register/' % reverse('login'), fetch_redirect_response=False)

    def test_get_shib_info_from_request(self):
        request = HttpRequest()
        request.META.update({'Shibboleth-sn': 'Jones', 'Shibboleth-givenName': 'Tom',
                             'Shibboleth-mail': 'tom_jones@school.edu'})
        shib_info = get_shib_info_from_request(request)
        self.assertEqual(shib_info['last_name'], 'Jones')
        self.assertEqual(shib_info['first_name'], 'Tom')
        self.assertEqual(shib_info['email'], 'tom_jones@school.edu')

    def test_register_get(self):
        auth_client = get_auth_client()
        degree = Degree.objects.create(abbreviation='Ph.D.', name='Doctorate')
        degree2 = Degree.objects.create(abbreviation='M.S.', name='Masters', degree_type=Degree.TYPES.masters)
        response = auth_client.get(reverse('register'), **{'Shibboleth-sn': 'Jones'})
        self.assertContains(response, 'Registration:')
        response_text = response.content.decode('utf8')
        last_name_input = '<input type="text" name="last_name" value="Jones" maxlength="190" class="textinput textInput" required id="id_last_name" />'
        self.assertInHTML(last_name_input, response_text)
        self.assertContains(response, 'Must match name on thesis or dissertation')
        self.assertContains(response, 'Department')
        self.assertContains(response, 'input type="radio" name="degree"')
        self.assertContains(response, 'Ph.D.')
        self.assertContains(response, 'M.S.')
        self.assertContains(response, 'submit')
        self.assertContains(response, 'Restrict access')
        self.assertNotContains(response, 'Netid')
        #test degree choices limited appropriately
        response = auth_client.get('%s?type=dissertation' % reverse('register'))
        self.assertContains(response, 'Must match name on dissertation</p>')
        self.assertContains(response, 'Ph.D.')
        self.assertNotContains(response, 'M.S.')
        self.assertContains(response, 'Restrict access to my dissertation for 2 years')
        response = auth_client.get('%s?type=thesis' % reverse('register'))
        self.assertContains(response, 'Must match name on thesis</p>')
        self.assertNotContains(response, 'Ph.D.')
        self.assertContains(response, 'M.S.')
        self.assertContains(response, 'Restrict access to my thesis for 2 years')

    def test_register_get_candidate_exists(self):
        embargo_unchecked = '<input type="checkbox" name="set_embargo" class="checkboxinput" id="id_set_embargo" />'
        embargo_checked = '<input type="checkbox" name="set_embargo" checked class="checkboxinput" id="id_set_embargo" />'
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('register'))
        self.assertContains(response, 'value="%s"' % LAST_NAME)
        self.assertContains(response, 'selected>%s</option>' % CURRENT_YEAR)
        self.assertInHTML(embargo_unchecked, response.content.decode('utf8'))
        self.candidate.embargo_end_year = CURRENT_YEAR + 2
        self.candidate.save()
        response = auth_client.get(reverse('register'))
        self.assertInHTML(embargo_checked, response.content.decode('utf8'))

    def _create_candidate_foreign_keys(self):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor')

    def test_email_field_required(self):
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        del data['email']
        data.update({'year': CURRENT_YEAR, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        email_required_msg = u'<span id="error_1_id_email" class="help-inline"><strong>This field is required.</strong></span>'
        self.assertInHTML(email_required_msg, response.content.decode('utf8'))

    def test_new_person_and_candidate_created_with_embargo(self):
        '''verify that new data for Person & Candidate gets saved properly (& redirected to candidate_home)'''
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data.update({'year': CURRENT_YEAR, 'department': self.dept.id, 'degree': self.degree.id,
                     'set_embargo': 'on'})
        response = auth_client.post(reverse('register'), data, follow=True, **{'Shibboleth-brownBannerID': '12345'})
        person = Person.objects.all()[0]
        self.assertEqual(person.netid, 'tjones@brown.edu') #make sure logged-in user netid was used, not the invalid parameter netid
        self.assertEqual(person.bannerid, '12345')
        self.assertEqual(person.last_name, LAST_NAME)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.year, CURRENT_YEAR)
        self.assertEqual(candidate.degree.abbreviation, 'Ph.D')
        self.assertEqual(candidate.embargo_end_year, CURRENT_YEAR + 2)
        self.assertRedirects(response, reverse('candidate_home'))

    def test_invalid_year(self):
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data.update({'year': 1816, 'department': self.dept.id, 'degree': self.degree.id,
                     'set_embargo': 'on'})
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(len(Candidate.objects.all()), 0)
        self.assertContains(response, '1816 is not one of the available choices.')

    def test_no_embargo(self):
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data.update({'year': CURRENT_YEAR, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.embargo_end_year, None)

    def test_register_and_edit_existing_person_by_netid(self):
        person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME)
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data['last_name'] = 'new last name'
        data.update({'year': CURRENT_YEAR, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(len(Person.objects.all()), 1)
        person = Person.objects.all()[0]
        self.assertEqual(person.last_name, 'new last name')
        self.assertEqual(len(Candidate.objects.all()), 1)
        candidate = Candidate.objects.get(person=person)
        self.assertEqual(candidate.year, CURRENT_YEAR)

    def test_register_and_edit_existing_person_by_orcid(self):
        person = Person.objects.create(orcid='1234567890', last_name=LAST_NAME)
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data['last_name'] = 'new last name'
        data.update({'year': CURRENT_YEAR, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(len(Person.objects.all()), 1)
        person = Person.objects.all()[0]
        self.assertEqual(person.last_name, 'new last name')
        self.assertEqual(len(Candidate.objects.all()), 1)
        candidate = Candidate.objects.get(person=person)
        self.assertEqual(candidate.year, CURRENT_YEAR)

    def test_edit_candidate_data(self):
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        candidate = Candidate.objects.create(person=person, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        data = self.person_data.copy()
        #change the last name - everything else stays the same
        data['last_name'] = 'new last name'
        data.update({'year': CURRENT_YEAR, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(len(Person.objects.all()), 1)
        person = Person.objects.all()[0]
        self.assertEqual(person.last_name, 'new last name')
        self.assertEqual(len(Candidate.objects.all()), 1)
        candidate = Candidate.objects.get(person=person)
        self.assertEqual(candidate.year, CURRENT_YEAR)

    def test_edit_candidate_remove_embargo(self):
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        candidate = Candidate.objects.create(person=person,
                                             year=CURRENT_YEAR,
                                             department=self.dept,
                                             degree=self.degree,
                                             embargo_end_year=(CURRENT_YEAR+2))
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.embargo_end_year, CURRENT_YEAR+2)
        data = self.person_data.copy()
        data.update({'year': CURRENT_YEAR, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.embargo_end_year, None)


class TestCandidateHome(TestCase, CandidateCreator):

    def test_candidate_home_auth(self):
        response = self.client.get(reverse('candidate_home'))
        self.assertRedirects(response, '%s?next=/candidate/' % reverse('login'), fetch_redirect_response=False)

    def test_candidate_not_registered(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertRedirects(response, reverse('register'))

    def test_candidate(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, '%s %s' % (FIRST_NAME, LAST_NAME))
        self.assertContains(response, 'Edit Profile</a>')
        self.assertContains(response, reverse('candidate_metadata'))
        self.assertContains(response, reverse('candidate_upload'))
        self.assertContains(response, 'Submit Cashier&#39;s Office receipt for dissertation fee')
        self.assertNotContains(response, 'Completed on ')

    def test_candidate_thesis_uploaded(self):
        self._create_candidate()
        add_file_to_thesis(self.candidate.thesis)
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, TEST_PDF_FILENAME)
        self.assertContains(response, reverse('candidate_upload'))

    def test_candidate_show_committee_members(self):
        self._create_candidate()
        advisor_person = Person.objects.create(last_name='johnson', first_name='bob')
        advisor = CommitteeMember.objects.create(person=advisor_person, role='advisor', department=self.dept)
        self.candidate.committee_members.add(advisor)
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, 'Advisor')

    def test_candidate_ready_to_submit(self):
        self._create_candidate()
        degree2 = Degree.objects.create(abbreviation='MS', name='Masters', degree_type=Degree.TYPES.masters)
        self.candidate.degree = degree2
        self.candidate.save()
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, 'Preview and Submit Thesis')

    def test_candidate_thesis_locked(self):
        #don't show links for changing information once the dissertation is locked
        self._create_candidate()
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        self.candidate.thesis.accept()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertNotContains(response, reverse('candidate_metadata'))
        self.assertNotContains(response, reverse('candidate_upload'))
        self.assertNotContains(response, reverse('candidate_committee'))
        self.assertNotContains(response, reverse('candidate_committee_remove', kwargs={'cm_id': self.committee_member.id}))

    def test_candidate_get_checklist_complete(self):
        self._create_candidate()
        self.candidate.gradschool_checklist.dissertation_fee = timezone.now()
        self.candidate.gradschool_checklist.bursar_receipt = timezone.now()
        self.candidate.gradschool_checklist.gradschool_exit_survey = timezone.now()
        self.candidate.gradschool_checklist.earned_docs_survey = timezone.now()
        self.candidate.gradschool_checklist.pages_submitted_to_gradschool = timezone.now()
        self.candidate.gradschool_checklist.save()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, 'Completed on ')


class TestCandidatePreviewSubmit(TestCase, CandidateCreator):

    def test_candidate_preview_auth(self):
        response = self.client.get(reverse('candidate_preview_submission'))
        self.assertRedirects(response, '%s?next=/candidate/preview/' % reverse('login'), fetch_redirect_response=False)

    def test_candidate_preview(self):
        self._create_candidate()
        self.candidate.committee_members.add(self.committee_member)
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        auth_client = get_auth_client()
        response = auth_client.post(reverse('candidate_preview_submission'))
        self.assertContains(response, 'Preview Your Dissertation')
        self.assertContains(response, 'Name:')
        self.assertContains(response, 'Title:')
        self.assertContains(response, 'Submit Your Dissertation')
        self.assertNotContains(response, 'Embargoed until %s' % (CURRENT_YEAR + 2))
        self.candidate.embargo_end_year = CURRENT_YEAR + 2
        self.candidate.save()
        response = auth_client.post(reverse('candidate_preview_submission'))
        self.assertContains(response, 'Embargoed until %s' % (CURRENT_YEAR + 2))

    def test_candidate_submit(self):
        self._create_candidate()
        self.candidate.committee_members.add(self.committee_member)
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        auth_client = get_auth_client()
        response = auth_client.post(reverse('candidate_submit'))
        self.assertRedirects(response, 'http://testserver/candidate/')
        self.assertEqual(Candidate.objects.all()[0].thesis.status, 'pending')


class TestCandidateUpload(TestCase, CandidateCreator):

    def test_upload_auth(self):
        response = self.client.get(reverse('candidate_upload'))
        self.assertRedirects(response, '%s?next=/candidate/upload/' % reverse('login'), fetch_redirect_response=False)

    def test_upload_get(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_upload'))
        self.assertContains(response, '%s %s' % (FIRST_NAME, LAST_NAME))
        self.assertContains(response, 'Upload Your Dissertation')

    def test_upload_thesis_locked(self):
        self._create_candidate()
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        self.candidate.thesis.accept()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_upload'))
        self.assertEqual(response.status_code, 403)
        response = auth_client.post(reverse('candidate_upload'))
        self.assertEqual(response.status_code, 403)

    def test_upload_post(self):
        self._create_candidate()
        auth_client = get_auth_client()
        self.assertEqual(len(Thesis.objects.all()), 1)
        with open(os.path.join(self.cur_dir, 'test_files', TEST_PDF_FILENAME), 'rb') as f:
            response = auth_client.post(reverse('candidate_upload'), {'thesis_file': f})
        self.assertEqual(len(Thesis.objects.all()), 1)
        self.assertEqual(Candidate.objects.all()[0].thesis.original_file_name, TEST_PDF_FILENAME)
        self.assertRedirects(response, reverse('candidate_home'))
        full_path = os.path.join(settings.MEDIA_ROOT, Candidate.objects.all()[0].thesis.current_file_name)
        self.assertTrue(os.path.exists(full_path), '%s doesn\'t exist' % full_path)

    def test_upload_bad_file(self):
        self._create_candidate()
        auth_client = get_auth_client()
        self.assertEqual(len(Thesis.objects.all()), 1)
        with open(os.path.join(self.cur_dir, 'test_files', 'test_obj'), 'rb') as f:
            response = auth_client.post(reverse('candidate_upload'), {'thesis_file': f})
            self.assertContains(response, 'Upload Your Dissertation')
            self.assertContains(response, 'file must be a PDF')
            self.assertFalse(Candidate.objects.all()[0].thesis.document)
            self.assertEqual(len(Thesis.objects.all()), 1)

    def test_upload_new_thesis_file(self):
        self._create_candidate()
        auth_client = get_auth_client()
        add_file_to_thesis(self.candidate.thesis)
        self.assertEqual(len(Thesis.objects.all()), 1)
        thesis = Candidate.objects.all()[0].thesis
        self.assertEqual(thesis.original_file_name, TEST_PDF_FILENAME)
        self.assertEqual(thesis.checksum, 'b1938fc5549d1b5b42c0b695baa76d5df5f81ac3')
        with open(os.path.join(self.cur_dir, 'test_files', 'test2.pdf'), 'rb') as f:
            response = auth_client.post(reverse('candidate_upload'), {'thesis_file': f})
            self.assertEqual(len(Thesis.objects.all()), 1)
            thesis = Candidate.objects.all()[0].thesis
            self.assertEqual(thesis.original_file_name, 'test2.pdf')
            self.assertEqual(thesis.checksum, '2ce252ec827258837e53b2b0bfb94141ba951f2e')


class TestCandidateMetadata(TestCase, CandidateCreator):

    def test_metadata_auth(self):
        response = self.client.get(reverse('candidate_metadata'))
        self.assertRedirects(response, '%s?next=/candidate/metadata/' % reverse('login'), fetch_redirect_response=False)

    def test_metadata_get(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_metadata'))
        self.assertContains(response, '%s %s' % (FIRST_NAME, LAST_NAME))
        self.assertContains(response, 'About Your Dissertation')
        self.assertContains(response, 'Title')

    def test_metadata_thesis_locked(self):
        self._create_candidate()
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        self.candidate.thesis.accept()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_metadata'))
        self.assertEqual(response.status_code, 403)
        response = auth_client.post(reverse('candidate_metadata'))
        self.assertEqual(response.status_code, 403)

    def test_metadata_post_incomplete_data(self):
        self._create_candidate()
        auth_client = get_auth_client()
        self.assertEqual(len(Thesis.objects.all()), 1)
        data = {'title':'tëst', 'abstract': 'tëst abstract'}
        response = auth_client.post(reverse('candidate_metadata'), data)
        self.assertContains(response, '<span id="error_1_id_keywords" class="help-inline"><strong>This field is required.')

    def test_metadata_post(self):
        self._create_candidate()
        auth_client = get_auth_client()
        self.assertEqual(len(Thesis.objects.all()), 1)
        k = Keyword.objects.create(text='tëst')
        data = {'title':'tëst', 'abstract': 'tëst abstract', 'keywords': [k.id, 'dog', 'fst12345%sSomething' % ID_VAL_SEPARATOR]}
        response = auth_client.post(reverse('candidate_metadata'), data, follow=True)
        self.assertRedirects(response, reverse('candidate_home'))
        self.assertEqual(len(Thesis.objects.all()), 1)
        self.assertEqual(Candidate.objects.all()[0].thesis.title, 'tëst')
        keywords = sorted([kw.text for kw in Candidate.objects.all()[0].thesis.keywords.all()])
        self.assertEqual(keywords, ['Something', 'dog', 'tëst'])
        self.assertNotContains(response, 'invisible characters')

    def _encode_multipart(self, data):
        #custom encoding method that handles bytes that way we want - django sees bytes input as a list of values
        lines = []
        def to_bytes(s):
            return force_bytes(s, settings.DEFAULT_CHARSET)
        for (key, value) in data.items():
            lines.extend(to_bytes(val) for val in [
                       '--%s' % BOUNDARY,
                       'Content-Disposition: form-data; name="%s"' % key,
                       '',
                       value
                   ])
        lines.extend([
            to_bytes('--%s--' % BOUNDARY),
            b'',
        ])
        return b'\r\n'.join(lines)

    def test_metadata_post_bad_encoding(self):
        #Try passing non-utf8 bytes and see what happens. Gets saved to the db, but it's mangled.
        self._create_candidate()
        auth_client = get_auth_client()
        self.assertEqual(len(Thesis.objects.all()), 1)
        k = Keyword.objects.create(text='tëst')
        abstract_utf16_bytes = 'tëst abstract'.encode('utf16')
        data = {'title': 'tëst', 'abstract': abstract_utf16_bytes, 'keywords': k.id}
        multipart_data = self._encode_multipart(data)
        self.assertTrue(abstract_utf16_bytes in multipart_data)
        #use generic(), because we can bypass the encoding step that post() does on the data
        response = auth_client.generic('POST', reverse('candidate_metadata'), multipart_data, MULTIPART_CONTENT)
        self.assertEqual(len(Thesis.objects.all()), 1)
        thesis = Candidate.objects.all()[0].thesis
        self.assertEqual(Candidate.objects.all()[0].thesis.title, 'tëst')
        abstract = Candidate.objects.all()[0].thesis.abstract
        self.assertTrue(isinstance(abstract, str))
        mangled_abstract = '��t\x00�\x00s\x00t\x00 \x00a\x00b\x00s\x00t\x00r\x00a\x00c\x00t\x00'
        self.assertEqual(abstract, mangled_abstract)
        self.assertNotEqual(abstract.encode('utf16'), abstract_utf16_bytes)

    def test_user_message_for_invalid_control_characters(self):
        self._create_candidate()
        auth_client = get_auth_client()
        k = Keyword.objects.create(text='tëst')
        data = {'title': 'tëst', 'abstract': 'tëst \x0cabstract', 'keywords': k.id}
        response = auth_client.post(reverse('candidate_metadata'), data, follow=True)
        self.assertContains(response, 'Your abstract contained invisible characters that we\'ve removed. Please make sure your abstract is correct in the information section below.')
        data = {'title': 'tëst \x0ctitle', 'abstract': 'tëst', 'keywords': k.id}
        response = auth_client.post(reverse('candidate_metadata'), data, follow=True)
        self.assertContains(response, 'Your title contained invisible characters that we\'ve removed. Please make sure your title is correct in the information section below.')

    def test_user_message_for_invalid_control_chars_in_keyword(self):
        self._create_candidate()
        auth_client = get_auth_client()
        data = {'title': 'title', 'abstract': 'tëst', 'keywords': 'tëst \x0ckeyword'}
        response = auth_client.post(reverse('candidate_metadata'), data, follow=True)
        self.assertContains(response, 'Your keywords contained invisible characters that we\'ve removed. Please make sure your keywords are correct in the information section below.')

    def test_user_message_for_invalid_control_chars_in_fast_keyword(self):
        self._create_candidate()
        auth_client = get_auth_client()
        data = {'title': 'title', 'abstract': 'tëst', 'keywords': 'fst12345\tSom\x0cething'}
        response = auth_client.post(reverse('candidate_metadata'), data, follow=True)
        self.assertContains(response, 'Your keywords contained invisible characters that we\'ve removed. Please make sure your keywords are correct in the information section below.')

    def test_metadata_post_thesis_already_exists(self):
        self._create_candidate()
        auth_client = get_auth_client()
        add_file_to_thesis(self.candidate.thesis)
        self.assertEqual(len(Thesis.objects.all()), 1)
        k = Keyword.objects.create(text='tëst')
        data = {'title': 'tëst', 'abstract': 'tëst abstract', 'keywords': k.id}
        response = auth_client.post(reverse('candidate_metadata'), data)
        self.assertEqual(len(Thesis.objects.all()), 1)
        thesis = Candidate.objects.all()[0].thesis
        self.assertEqual(thesis.title, 'tëst')
        self.assertEqual(thesis.original_file_name, TEST_PDF_FILENAME)


class TestCommitteeMembers(TestCase, CandidateCreator):

    def test_committee_members_auth(self):
        response = self.client.get(reverse('candidate_committee'))
        self.assertRedirects(response, '%s?next=/candidate/committee/' % reverse('login'), fetch_redirect_response=False)

    def test_committee_members_get(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_committee'))
        self.assertContains(response, 'About Your Committee')
        self.assertContains(response, 'Last Name')
        self.assertContains(response, 'Brown Department')

    def test_committee_members_thesis_locked(self):
        self._create_candidate()
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        self.candidate.thesis.accept()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_committee'))
        self.assertEqual(response.status_code, 403)
        response = auth_client.post(reverse('candidate_committee'))
        self.assertEqual(response.status_code, 403)

    def test_add_committee_member(self):
        self._create_candidate()
        auth_client = get_auth_client()
        post_data = {'last_name': 'smith', 'first_name': 'bob', 'role': 'reader', 'department': self.dept.id}
        response = auth_client.post(reverse('candidate_committee'), post_data)
        self.assertEqual(Candidate.objects.all()[0].committee_members.all()[0].person.last_name, 'smith')
        self.assertEqual(Candidate.objects.all()[0].committee_members.all()[0].role, 'reader')

    def test_committee_member_remove_auth(self):
        self._create_candidate()
        cm = CommitteeMember.objects.create(person=self.person, department=self.dept)
        response = self.client.get(reverse('candidate_committee_remove', kwargs={'cm_id': cm.id}))
        self.assertRedirects(response, '%s?next=/candidate/committee/%s/remove/' % (reverse('login'), cm.id), fetch_redirect_response=False)

    def test_remove_committee_member(self):
        self._create_candidate()
        self.candidate.committee_members.add(self.committee_member)
        self.assertEqual(len(self.candidate.committee_members.all()), 1)
        auth_client = get_auth_client()
        response = auth_client.post(reverse('candidate_committee_remove', kwargs={'cm_id': self.committee_member.id}))
        self.assertEqual(len(self.candidate.committee_members.all()), 0)


class TestStaffReview(TestCase, CandidateCreator):

    def test_login_required(self):
        response = self.client.get(reverse('staff_home'))
        self.assertRedirects(response, '%s?next=/review/' % reverse('login'), fetch_redirect_response=False)

    def test_permission_required(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('staff_home'))
        self.assertEqual(response.status_code, 403)

    def test_staff_home_get(self):
        staff_client = get_staff_client()
        response = staff_client.get(reverse('staff_home'))
        self.assertRedirects(response, reverse('review_candidates', kwargs={'status': 'all'}))

    def test_view_candidates_permission_required(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('review_candidates', kwargs={'status': 'all'}))
        self.assertEqual(response.status_code, 403)

    def test_view_candidates_all(self):
        self._create_candidate()
        thesis = Thesis.objects.all()[0]
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        self.candidate.committee_members.add(self.committee_member)
        thesis.submit()
        staff_client = get_staff_client()
        response = staff_client.get(reverse('review_candidates', kwargs={'status': 'all'}))
        self.assertContains(response, '>Status</a>')
        self.assertContains(response, '%s, %s' % (LAST_NAME, FIRST_NAME))
        self.assertContains(response, 'Awaiting ')

    def test_view_candidates_in_progress(self):
        self._create_candidate()
        self.candidate.thesis.title = 'tëst'
        self.candidate.thesis.save()
        staff_client = get_staff_client()
        response = staff_client.get(reverse('review_candidates', kwargs={'status': 'in_progress'}))
        self.assertContains(response, '>Dissertation Title</a>')
        self.assertContains(response, 'tëst')

    def test_view_candidates_other_statuses(self):
        staff_client = get_staff_client()
        response = staff_client.get(reverse('review_candidates', kwargs={'status': 'awaiting_gradschool'}))
        self.assertEqual(response.status_code, 200)
        response = staff_client.get(reverse('review_candidates', kwargs={'status': 'dissertation_rejected'}))
        self.assertEqual(response.status_code, 200)
        response = staff_client.get(reverse('review_candidates', kwargs={'status': 'paperwork_incomplete'}))
        self.assertEqual(response.status_code, 200)
        response = staff_client.get(reverse('review_candidates', kwargs={'status': 'complete'}))
        self.assertEqual(response.status_code, 200)

    def test_view_candidates_sorted(self):
        self._create_candidate()
        p = Person.objects.create(netid='rsmith@brown.edu', last_name='smith', email='r_smith@brown.edu')
        c = Candidate.objects.create(person=p, department=Department.objects.create(name='Anthropology', bdr_collection_id='2'),
                year=CURRENT_YEAR, degree=self.degree)
        staff_client = get_staff_client()
        response = staff_client.get('%s?sort_by=department' % reverse('review_candidates', kwargs={'status': 'all'}))
        self.assertEqual(response.status_code, 200)
        #tests passing in the sort_by param, but not really sure how to completely verify result


class TestStaffApproveThesis(TestCase, CandidateCreator):

    def test_permission_required(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('approve', kwargs={'candidate_id': self.candidate.id}))
        self.assertEqual(response.status_code, 403)

    def test_approve_get(self):
        self._create_candidate()
        staff_client = get_staff_client()
        response = staff_client.get(reverse('approve', kwargs={'candidate_id': self.candidate.id}))
        self.assertContains(response, '%s %s' % (FIRST_NAME, LAST_NAME))
        self.assertContains(response, '<input type="checkbox" name="dissertation_fee" />Received')
        self.assertContains(response, 'View Dissertation')
        self.assertContains(response, 'View Abstract')
        self.assertNotContains(response, 'Title page issue')
        self.assertNotContains(response, 'Received on ')
        now = timezone.now()
        self.candidate.gradschool_checklist.dissertation_fee = now
        self.candidate.gradschool_checklist.save()
        response = staff_client.get(reverse('approve', kwargs={'candidate_id': self.candidate.id}))
        self.assertNotContains(response, '<input type="checkbox" name="dissertation_fee" />Received')
        self.assertContains(response, 'Received on ')

    def test_approve_post(self):
        staff_client = get_staff_client()
        self._create_candidate()
        self.candidate.gradschool_checklist.earned_docs_survey = timezone.now()
        self.candidate.gradschool_checklist.save()
        post_data = {'dissertation_fee': True, 'bursar_receipt': True, 'pages_submitted_to_gradschool': True}
        response = staff_client.post(reverse('approve', kwargs={'candidate_id': self.candidate.id}), post_data)
        self.assertEqual(Candidate.objects.all()[0].gradschool_checklist.dissertation_fee.date(), timezone.now().date())
        self.assertEqual(Candidate.objects.all()[0].gradschool_checklist.bursar_receipt.date(), timezone.now().date())
        self.assertEqual(Candidate.objects.all()[0].gradschool_checklist.earned_docs_survey.date(), timezone.now().date())
        self.assertEqual(Candidate.objects.all()[0].gradschool_checklist.pages_submitted_to_gradschool.date(), timezone.now().date())
        self.assertRedirects(response, reverse('staff_home'), fetch_redirect_response=False)

    def test_format_post_perms(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.post(reverse('format_post', kwargs={'candidate_id': self.candidate.id}))
        self.assertEqual(response.status_code, 403)

    def test_format_post(self):
        self._create_candidate()
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        staff_client = get_staff_client()
        post_data = {'title_page_issue': True, 'signature_page_issue': True, 'signature_page_comment': 'Test comment',
                'accept_diss': 'Approve'}
        url = reverse('format_post', kwargs={'candidate_id': self.candidate.id})
        response = staff_client.post(url, post_data)
        self.assertRedirects(response, reverse('approve', kwargs={'candidate_id': self.candidate.id}))
        self.assertEqual(Candidate.objects.all()[0].thesis.format_checklist.title_page_issue, True)
        self.assertEqual(Candidate.objects.all()[0].thesis.status, Thesis.STATUS_CHOICES.accepted)

    def test_format_post_reject(self):
        self._create_candidate()
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        staff_client = get_staff_client()
        post_data = {'title_page_issue': True, 'signature_page_issue': True, 'signature_page_comment': 'Test comment',
                'reject_diss': 'Reject'}
        url = reverse('format_post', kwargs={'candidate_id': self.candidate.id})
        response = staff_client.post(url, post_data)
        self.assertEqual(Candidate.objects.all()[0].thesis.status, Thesis.STATUS_CHOICES.rejected)


class TestViewInfo(TestCase, CandidateCreator):

    def test_view_abstract_perm_required(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('abstract', kwargs={'candidate_id': self.candidate.id}))
        self.assertEqual(response.status_code, 403)

    def test_view_abstract(self):
        self._create_candidate()
        add_metadata_to_thesis(self.candidate.thesis)
        staff_client = get_staff_client()
        response = staff_client.get(reverse('abstract', kwargs={'candidate_id': self.candidate.id}))
        self.assertContains(response, 'test abstract')

    def test_view_file_login_required(self):
        self._create_candidate()
        url = reverse('view_file', kwargs={'candidate_id': self.candidate.id})
        response = self.client.get(url)
        self.assertRedirects(response, '%s?next=%s' % (reverse('login'), url), fetch_redirect_response=False)

    def test_view_file(self):
        self._create_candidate()
        auth_client = get_auth_client()
        with open(os.path.join(self.cur_dir, 'test_files', 'test2.pdf'), 'rb') as f:
            response = auth_client.post(reverse('candidate_upload'), {'thesis_file': f})
        response = auth_client.get(reverse('view_file', kwargs={'candidate_id': self.candidate.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_file_no_file(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('view_file', kwargs={'candidate_id': self.candidate.id}))
        self.assertEqual(response.status_code, 200)


class TestAutocompleteKeywords(TestCase):

    def test_login(self):
        response = self.client.get(reverse('autocomplete_keywords'))
        self.assertRedirects(response, '%s?next=/autocomplete/keywords/' % reverse('login'), fetch_redirect_response=False)

    def test_previously_used(self):
        #test empty
        results = _get_previously_used(Keyword, 'test')
        self.assertEqual(results, [])
        #now test with a result
        k = Keyword.objects.create(text='tëst')
        results = _get_previously_used(Keyword, 'test')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'Previously Used')
        self.assertEqual(results[0]['children'][0]['id'], k.id)
        self.assertEqual(results[0]['children'][0]['text'], k.text)

    @responses.activate
    def test_fast_lookup(self):
        responses.add(responses.GET,  'http://fast.oclc.org/searchfast/fastsuggest',
                 body=json.dumps(responses_data.FAST_PYTHON_DATA),
                 status=200,
                 content_type='application/json'
             )
        fast_results = _get_fast_results('python')
        self.assertEqual(fast_results[0]['text'], 'FAST results')
        self.assertEqual(fast_results[0]['children'][0]['id'], 'fst01084736%sPython (Computer program language)' % ID_VAL_SEPARATOR)
        self.assertEqual(fast_results[0]['children'][0]['text'], 'Python (Computer program language)')

    @responses.activate
    def test_no_fast_results(self):
        responses.add(responses.GET,  'http://fast.oclc.org/searchfast/fastsuggest',
                body=json.dumps(responses_data.FAST_NO_RESULTS_DATA),
                status=200,
                content_type='application/json'
            )
        fast_results = _get_fast_results('python01234')
        self.assertEqual(fast_results, [])

    @responses.activate
    def test_fast_timeout(self):
        from requests.exceptions import Timeout
        timeout_exc = Timeout()
        responses.add(responses.GET,  'http://fast.oclc.org/searchfast/fastsuggest',
                body=timeout_exc,
            )
        fast_results = _get_fast_results('python')
        self.assertEqual(fast_results[0]['text'], 'FAST results')
        self.assertEqual(fast_results[0]['children'][0]['id'], '')
        self.assertEqual(fast_results[0]['children'][0]['text'], 'Error retrieving FAST results.')

    def test_fast_error(self):
        with self.settings(FAST_LOOKUP_BASE_URL='http://localhost/fast'):
            fast_results = _get_fast_results('python')
            self.assertEqual(fast_results[0]['text'], 'FAST results')
            self.assertEqual(fast_results[0]['children'][0]['id'], '')
            self.assertEqual(fast_results[0]['children'][0]['text'], 'Error retrieving FAST results.')


    def test_autocomplete_keywords(self):
        k = Keyword.objects.create(text='tëst')
        auth_client = get_auth_client()
        response = auth_client.get('%s?term=test' % reverse('autocomplete_keywords'))
        response_data = json.loads(response.content)
        self.assertEqual(response_data['err'], 'nil')
        self.assertEqual(response_data['results'][0]['text'], 'Previously Used')
        self.assertEqual(response_data['results'][0]['children'][0]['text'], k.text)
        self.assertEqual(response_data['results'][1]['text'], 'FAST results')

