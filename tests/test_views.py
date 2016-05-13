# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
from django.contrib.auth.models import User, Permission
from django.core.files import File
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpRequest
from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from tests.test_client import ETDTestClient
from tests.test_models import LAST_NAME, FIRST_NAME, add_file_to_thesis, add_metadata_to_thesis
from etd_app.models import Person, Candidate, CommitteeMember, Department, Degree, Thesis, Keyword
from etd_app.views import get_shib_info_from_request, _get_previously_used, _get_fast_results
from etd_app.widgets import ID_VAL_SEPARATOR


def get_auth_client():
    user = User.objects.create_user('tjones@brown.edu', 'pw')
    auth_client = ETDTestClient()
    auth_client.force_login(user)
    return auth_client


def get_staff_client():
    user = User.objects.create_user('staff@brown.edu', 'pw')
    change_candidate_perm = Permission.objects.get(codename='change_candidate')
    user.user_permissions.add(change_candidate_perm)
    staff_client = ETDTestClient()
    staff_client.force_login(user)
    return staff_client


class TestStaticViews(SimpleTestCase):

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<title>Electronic Theses & Dissertations at Brown University')
        self.assertContains(response, 'Ph.D. candidates at Brown must file their dissertations electronically.')
        self.assertContains(response, 'Login or Register')
        self.assertContains(response, 'Staff Login')

    def test_overview(self):
        response = self.client.get(reverse('overview'))
        self.assertContains(response, 'Submission Overview')

    def test_faq(self):
        response = self.client.get(reverse('faq'))
        self.assertContains(response, 'Where are Brown’s ETDs available?')

    def test_tutorials(self):
        response = self.client.get(reverse('tutorials'))
        self.assertContains(response, 'Online Tutorials')

    def test_copyright(self):
        response = self.client.get(reverse('copyright'))
        self.assertContains(response, 'You own the copyright to your dissertation')


class CandidateCreator(object):
    '''mixin object for creating candidates'''

    @property
    def cur_dir(self):
        return os.path.dirname(os.path.abspath(__file__))

    def _create_candidate(self):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor')
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, first_name=FIRST_NAME,
                email='tom_jones@brown.edu')
        cm_person = Person.objects.create(last_name='Smith')
        self.committee_member = CommitteeMember.objects.create(person=cm_person, department=self.dept)
        self.candidate = Candidate.objects.create(person=self.person, year=2016, department=self.dept, degree=self.degree)


class TestRegister(TestCase, CandidateCreator):

    def setUp(self):
        #set an incorrect netid here, to make sure it's read from the username instead of
        #   the passed in value - we don't want someone to be able to register for a different user.
        self.person_data = {'netid': 'wrongid@brown.edu', 'orcid': '1234567890',
                'last_name': LAST_NAME, 'first_name': FIRST_NAME,
                'address_street': '123 Some Rd.', 'address_city': 'Ville',
                'address_state': 'RI', 'address_zip': '12345-5423',
                'email': 'tomjones@brown.edu', 'phone': '401-123-1234'}

    def test_register_auth(self):
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, '%s/?next=/register/' % settings.LOGIN_URL, fetch_redirect_response=False)

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
        response = auth_client.get(reverse('register'), **{'Shibboleth-sn': 'Jones'})
        self.assertContains(response, 'Registration:')
        self.assertContains(response, '<input class="textinput textInput" id="id_last_name" maxlength="190" name="last_name" type="text" value="Jones" />')
        self.assertContains(response, 'Department')
        self.assertContains(response, 'submit')
        self.assertContains(response, 'Restrict access')
        self.assertNotContains(response, 'Netid')

    def test_register_get_candidate_exists(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('register'))
        self.assertContains(response, 'value="%s"' % LAST_NAME)
        self.assertContains(response, 'selected="selected">2016</option>')

    def _create_candidate_foreign_keys(self):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor')

    def test_new_person_and_candidate_created_with_embargo(self):
        '''verify that new data for Person & Candidate gets saved properly (& redirected to candidate_home)'''
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data.update({'year': 2016, 'department': self.dept.id, 'degree': self.degree.id,
                     'set_embargo': 'on'})
        response = auth_client.post(reverse('register'), data, follow=True)
        person = Person.objects.all()[0]
        self.assertEqual(person.netid, 'tjones@brown.edu') #make sure logged-in user netid was used, not the invalid parameter netid
        self.assertEqual(person.last_name, LAST_NAME)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.year, 2016)
        self.assertEqual(candidate.degree.abbreviation, 'Ph.D')
        self.assertEqual(candidate.embargo_end_year, 2018)
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
        data.update({'year': 2016, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.embargo_end_year, None)

    def test_register_and_edit_existing_person_by_netid(self):
        person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME)
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data['last_name'] = 'new last name'
        data.update({'year': 2016, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(len(Person.objects.all()), 1)
        person = Person.objects.all()[0]
        self.assertEqual(person.last_name, 'new last name')
        self.assertEqual(len(Candidate.objects.all()), 1)
        candidate = Candidate.objects.get(person=person)
        self.assertEqual(candidate.year, 2016)

    def test_register_and_edit_existing_person_by_orcid(self):
        person = Person.objects.create(orcid='1234567890', last_name=LAST_NAME)
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        data = self.person_data.copy()
        data['last_name'] = 'new last name'
        data.update({'year': 2016, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(len(Person.objects.all()), 1)
        person = Person.objects.all()[0]
        self.assertEqual(person.last_name, 'new last name')
        self.assertEqual(len(Candidate.objects.all()), 1)
        candidate = Candidate.objects.get(person=person)
        self.assertEqual(candidate.year, 2016)

    def test_edit_candidate_data(self):
        auth_client = get_auth_client()
        self._create_candidate_foreign_keys()
        person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        candidate = Candidate.objects.create(person=person, year=2016, department=self.dept, degree=self.degree)
        data = self.person_data.copy()
        data['last_name'] = 'new last name'
        data.update({'year': 2017, 'department': self.dept.id, 'degree': self.degree.id})
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(len(Person.objects.all()), 1)
        person = Person.objects.all()[0]
        self.assertEqual(person.last_name, 'new last name')
        self.assertEqual(len(Candidate.objects.all()), 1)
        candidate = Candidate.objects.get(person=person)
        self.assertEqual(candidate.year, 2017)


class TestCandidateHome(TestCase, CandidateCreator):

    def test_candidate_home_auth(self):
        response = self.client.get(reverse('candidate_home'))
        self.assertRedirects(response, '%s/?next=/candidate/' % settings.LOGIN_URL, fetch_redirect_response=False)

    def test_candidate_get(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, '%s %s' % (FIRST_NAME, LAST_NAME))
        self.assertContains(response, 'Edit Profile</a>')
        self.assertContains(response, 'Edit information about your dissertation')
        self.assertContains(response, 'Upload dissertation file (PDF)')
        self.assertContains(response, 'Submit Cashier\'s Office receipt for dissertation fee')
        self.assertNotContains(response, 'Completed on ')

    def test_candidate_thesis_locked(self):
        self._create_candidate()
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        self.candidate.thesis.accept()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertNotContains(response, 'Edit information about your dissertation')
        self.assertNotContains(response, '">Upload ')

    def test_candidate_get_with_thesis(self):
        self._create_candidate()
        add_file_to_thesis(self.candidate.thesis)
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, 'test.pdf')
        self.assertContains(response, 'Upload new dissertation file (PDF)')

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

    def test_candidate_get_committee_members(self):
        self._create_candidate()
        advisor_person = Person.objects.create(last_name='johnson', first_name='bob')
        advisor = CommitteeMember.objects.create(person=advisor_person, role='advisor', department=self.dept)
        self.candidate.committee_members.add(advisor)
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, 'Advisor')

    def test_candidate_get_not_registered(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertRedirects(response, reverse('register'))

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
        self.assertRedirects(response, '%s/?next=/candidate/upload/' % settings.LOGIN_URL, fetch_redirect_response=False)

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
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            response = auth_client.post(reverse('candidate_upload'), {'thesis_file': f})
            self.assertEqual(len(Thesis.objects.all()), 1)
            self.assertEqual(Candidate.objects.all()[0].thesis.file_name, 'test.pdf')
            self.assertRedirects(response, reverse('candidate_home'))

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
        self.assertEqual(thesis.file_name, 'test.pdf')
        self.assertEqual(thesis.checksum, 'b1938fc5549d1b5b42c0b695baa76d5df5f81ac3')
        with open(os.path.join(self.cur_dir, 'test_files', 'test2.pdf'), 'rb') as f:
            response = auth_client.post(reverse('candidate_upload'), {'thesis_file': f})
            self.assertEqual(len(Thesis.objects.all()), 1)
            thesis = Candidate.objects.all()[0].thesis
            self.assertEqual(thesis.file_name, 'test2.pdf')
            self.assertEqual(thesis.checksum, '2ce252ec827258837e53b2b0bfb94141ba951f2e')


class TestCandidateMetadata(TestCase, CandidateCreator):

    def test_metadata_auth(self):
        response = self.client.get(reverse('candidate_metadata'))
        self.assertRedirects(response, '%s/?next=/candidate/metadata/' % settings.LOGIN_URL, fetch_redirect_response=False)

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

    def test_metadata_post(self):
        self._create_candidate()
        auth_client = get_auth_client()
        self.assertEqual(len(Thesis.objects.all()), 1)
        k = Keyword.objects.create(text='tëst')
        data = {'title': 'tëst', 'abstract': 'tëst abstract', 'keywords': k.id}
        response = auth_client.post(reverse('candidate_metadata'), data)
        self.assertRedirects(response, reverse('candidate_home'))
        self.assertEqual(len(Thesis.objects.all()), 1)
        self.assertEqual(Candidate.objects.all()[0].thesis.title, 'tëst')

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
        self.assertEqual(thesis.file_name, 'test.pdf')


class TestCommitteeMembers(TestCase, CandidateCreator):

    def test_committee_members_auth(self):
        response = self.client.get(reverse('candidate_committee'))
        self.assertRedirects(response, '%s/?next=/candidate/committee/' % settings.LOGIN_URL, fetch_redirect_response=False)

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
        self.assertRedirects(response, '%s/?next=/candidate/committee/%s/remove/' % (settings.LOGIN_URL, cm.id), fetch_redirect_response=False)

    def test_remove_committee_member(self):
        self._create_candidate()
        self.candidate.committee_members.add(self.committee_member)
        self.assertEqual(len(CommitteeMember.objects.all()), 1)
        self.assertEqual(len(self.candidate.committee_members.all()), 1)
        auth_client = get_auth_client()
        response = auth_client.post(reverse('candidate_committee_remove', kwargs={'cm_id': self.committee_member.id}))
        self.assertEqual(len(CommitteeMember.objects.all()), 1)
        self.assertEqual(len(self.candidate.committee_members.all()), 0)


class TestStaffReview(TestCase, CandidateCreator):

    def test_login_required(self):
        response = self.client.get(reverse('staff_home'))
        self.assertRedirects(response, '%s/?next=/review/' % settings.LOGIN_URL, fetch_redirect_response=False)

    def test_permission_required(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('staff_home'))
        self.assertEqual(response.status_code, 403)

    def test_staff_home_get(self):
        staff_client = get_staff_client()
        response = staff_client.get(reverse('staff_home'))
        self.assertContains(response, 'View candidates by status')

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
        c = Candidate.objects.create(person=p, department=Department.objects.create(name='Anthropology'),
                year=2016, degree=self.degree)
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
        self.assertRedirects(response, reverse('staff_home'))

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
        self.assertEqual(Candidate.objects.all()[0].thesis.status, 'accepted')

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
        self.assertEqual(Candidate.objects.all()[0].thesis.status, 'rejected')


class TestAutocompleteKeywords(TestCase):

    def test_login(self):
        response = self.client.get(reverse('autocomplete_keywords'))
        self.assertRedirects(response, '%s/?next=/autocomplete/keywords/' % settings.LOGIN_URL, fetch_redirect_response=False)

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

    def test_fast_lookup(self):
        fast_results = _get_fast_results('python')
        self.assertEqual(fast_results[0]['text'], 'FAST results')
        self.assertEqual(fast_results[0]['children'][0]['id'], 'fst01084736%sPython (Computer program language)' % ID_VAL_SEPARATOR)
        self.assertEqual(fast_results[0]['children'][0]['text'], 'Python (Computer program language)')
        #now test fast error
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
        self.assertEqual(response_data['results'][1]['text'], 'FAST results')
