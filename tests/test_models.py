from datetime import date, timedelta
import os
from django.core import mail
from django.core.files import File
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from etd_app.models import (
        Person,
        DuplicateNetidException,
        DuplicateOrcidException,
        DuplicateEmailException,
        DuplicateBannerIdException,
        Department,
        Degree,
        CandidateException,
        Candidate,
        GradschoolChecklist,
        CommitteeMemberException,
        CommitteeMember,
        KeywordException,
        Keyword,
        ThesisException,
        Thesis,
    )


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_YEAR = date.today().year
LAST_NAME = 'Jonës'
FIRST_NAME = 'T©m'
COMPOSED_TEXT = 'tëst'
DECOMPOSED_TEXT = 'tëst'
TEST_PDF_FILENAME = 'iñtërnâtiônàlĭzætiøn.pdf'


def complete_gradschool_checklist(candidate):
    candidate.gradschool_checklist.bursar_receipt = timezone.now()
    candidate.gradschool_checklist.pages_submitted_to_gradschool = timezone.now()
    if candidate.degree.degree_type == Degree.TYPES.doctorate:
        candidate.gradschool_checklist.gradschool_exit_survey = timezone.now()
        candidate.gradschool_checklist.earned_docs_survey = timezone.now()
    candidate.gradschool_checklist.save()


class TestPerson(TestCase):

    def test_person_create(self):
        netid = 'tjones@brown.edu'
        Person.objects.create(netid=netid, last_name=LAST_NAME, first_name=FIRST_NAME, orcid='', email='', bannerid='')
        person = Person.objects.all()[0]
        self.assertEqual(person.netid, netid)
        self.assertEqual(person.last_name, LAST_NAME)
        self.assertEqual(person.first_name, FIRST_NAME)
        self.assertEqual(person.orcid, None)
        self.assertEqual(person.email, None)
        self.assertEqual(person.bannerid, None)

    def test_formatted_name(self):
        p = Person.objects.create(last_name=LAST_NAME, first_name=FIRST_NAME, middle='Middle')
        self.assertEqual(p.get_formatted_name(), '%s, %s Middle' % (LAST_NAME, FIRST_NAME))
        p2 = Person.objects.create(last_name=LAST_NAME, first_name=FIRST_NAME)
        self.assertEqual(p2.get_formatted_name(), '%s, %s' % (LAST_NAME, FIRST_NAME))
        p3 = Person.objects.create(last_name=LAST_NAME)
        self.assertEqual(p3.get_formatted_name(), '%s' % LAST_NAME)

    def test_netid_optional(self):
        p = Person.objects.create()
        self.assertEqual(Person.objects.all()[0].netid, None)

    def test_netid_unique(self):
        netid = 'tjones@brown.edu'
        Person.objects.create(netid=netid)
        with self.assertRaises(DuplicateNetidException):
            Person.objects.create(netid=netid)

    def test_orcid_unique(self):
        orcid = '0000-0002-5286-384X'
        Person.objects.create(orcid=orcid)
        with self.assertRaises(DuplicateOrcidException):
            Person.objects.create(orcid=orcid)

    def test_email_unique(self):
        email = 'tom_jones@brown.edu'
        Person.objects.create(email=email)
        with self.assertRaises(DuplicateEmailException):
            Person.objects.create(email=email)

    def test_banner_id_unique(self):
        banner_id = '12345'
        Person.objects.create(bannerid=banner_id)
        with self.assertRaises(DuplicateBannerIdException):
            Person.objects.create(bannerid=banner_id)

    def test_netid_allow_multiple_blank(self):
        Person.objects.create()
        Person.objects.create()
        self.assertEqual(Person.objects.all()[0].netid, None)
        self.assertEqual(Person.objects.all()[1].netid, None)

    def test_utf8mb4_char_in_name(self):
        last_name = 'last𝌆name'
        Person.objects.create(last_name=last_name)
        self.assertEqual(Person.objects.all()[0].last_name, last_name)


class TestDepartment(TestCase):

    def test_create(self):
        Department.objects.create(name='tëst dept')
        self.assertEqual(Department.objects.all()[0].name, 'tëst dept')

    def test_collection_id(self):
        Department.objects.create(name='test', bdr_collection_id='111')
        self.assertEqual(Department.objects.all()[0].bdr_collection_id, '111')

    def test_multiple_null_collection_ids(self):
        Department.objects.create(name='tëst dept')
        Department.objects.create(name='tëst dept 2')
        self.assertEqual(len(Department.objects.all()), 2)
        self.assertEqual(Department.objects.all()[0].bdr_collection_id, None)
        self.assertEqual(Department.objects.all()[1].bdr_collection_id, None)

    def test_unique(self):
        name = 'tëst dept'
        Department.objects.create(name=name)
        with self.assertRaises(IntegrityError):
            Department.objects.create(name=name)


class TestDegree(TestCase):

    def setUp(self):
        Degree.objects.create(abbreviation='Ph.D.', name='Doctor of Philosophy')

    def test_create(self):
        self.assertEqual(Degree.objects.all()[0].abbreviation, 'Ph.D.')
        self.assertEqual(Degree.objects.all()[0].name, 'Doctor of Philosophy')
        self.assertEqual(Degree.objects.all()[0].degree_type, Degree.TYPES.doctorate)

    def test_unique_abbr(self):
        with self.assertRaises(IntegrityError):
            Degree.objects.create(abbreviation='Ph.D.', name='Doctor of Philosophy 2')

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            Degree.objects.create(abbreviation='Ph.D. 2', name='Doctor of Philosophy')

    def test_degree_type_adjective(self):
        self.assertEqual(Degree.objects.all()[0].degree_type_adjective, 'doctoral')
        d = Degree.objects.create(abbreviation='M.S.', name='Masters', degree_type=Degree.TYPES.masters)
        self.assertEqual(d.degree_type_adjective, 'masters')


class TestGradschoolChecklist(TestCase):

    def setUp(self):
        self.dept = Department.objects.create(name='Engineering')

    def test_doctorate_complete(self):
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor of Philosophy')
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        candidate = Candidate.objects.create(person=self.person, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        self.assertFalse(candidate.gradschool_checklist.complete())
        #test status() here as well
        self.assertEqual(candidate.gradschool_checklist.status(), 'Incomplete')
        complete_gradschool_checklist(candidate)
        self.assertTrue(candidate.gradschool_checklist.complete())
        self.assertFalse(candidate.gradschool_checklist.complete(dt=date.today()-timedelta(days=1)))
        self.assertEqual(candidate.gradschool_checklist.status(), 'Complete')

    def test_masters_complete(self):
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor of Philosophy', degree_type=Degree.TYPES.masters)
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        candidate = Candidate.objects.create(person=self.person, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        self.assertEqual(candidate.gradschool_checklist.complete(), False)
        complete_gradschool_checklist(candidate)
        self.assertEqual(candidate.gradschool_checklist.complete(), True)

    def test_get_items_doctorate(self):
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor of Philosophy')
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        candidate = Candidate.objects.create(person=self.person, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        display_items = candidate.gradschool_checklist.get_items()
        self.assertEqual(len(display_items), 3)
        # self.assertEqual(display_items[0]['display'], 'Submit Bursar\'s Office receipt (white) showing that all outstanding debts have been paid')
        self.assertEqual(display_items[0]['display'], 'Submit title page, abstract, and signature pages to Graduate School')

    def test_get_items_masters(self):
        self.degree = Degree.objects.create(abbreviation='MS', name='Masters', degree_type=Degree.TYPES.masters)
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        candidate = Candidate.objects.create(person=self.person, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        display_items = candidate.gradschool_checklist.get_items()
        self.assertEqual(len(display_items), 1)
        # self.assertEqual(display_items[0]['display'], 'Submit Bursar\'s Office receipt (white) showing that all outstanding debts have been paid')
        self.assertEqual(display_items[0]['display'], 'Submit title page and signature pages to Graduate School')


class TestCandidate(TransactionTestCase):

    def setUp(self):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D')
        self.masters_degree = Degree.objects.create(abbreviation='AM', name='Masters', degree_type=Degree.TYPES.masters)

    def test_person_must_have_netid(self):
        #if a person is becoming a candidate, they must have a Brown netid
        p = Person.objects.create(last_name=LAST_NAME)
        with self.assertRaises(CandidateException) as cm:
            Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        self.assertEqual(str(cm.exception), 'candidate must have a Brown netid')

    def test_create_candidate(self):
        p = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid='rsmith@brown.edu', last_name='smith')
        Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.person.netid, 'tjones@brown.edu')
        self.assertEqual(candidate.date_registered, date.today())
        self.assertEqual(candidate.embargo_end_year, None)
        self.assertEqual(candidate.thesis.status, 'not_submitted')
        self.assertEqual(candidate.gradschool_checklist.dissertation_fee, None)
        candidate.committee_members.add(CommitteeMember.objects.create(person=p2, department=self.dept))
        created_candidate = Candidate.objects.all()[0]
        self.assertEqual(created_candidate.committee_members.all()[0].person.last_name, 'smith')
        self.assertEqual(str(created_candidate), f'Jonës (Ph.D - {CURRENT_YEAR})')

    def test_two_candidacies(self):
        p = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.masters_degree)
        Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        candidacies = Candidate.objects.filter(person=p)
        self.assertEqual(len(candidacies), 2)

    def test_year_validation(self):
        p = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        with self.assertRaises(Exception):
            Candidate.objects.create(person=p, year='abc', department=self.dept, degree=self.degree)

    def test_get_candidates_all(self):
        p = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid='rjones@brown.edu', last_name='jones', email='r_jones@brown.edu')
        Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        Candidate.objects.create(person=p2, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        self.assertEqual(len(Candidate.get_candidates_by_status('all')), 2)

    def test_get_candidates_status(self):
        p = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid='rsmith@brown.edu', last_name='smith', email='r_smith@brown.edu')
        p3 = Person.objects.create(last_name='thomson')
        c = Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        cm = CommitteeMember.objects.create(person=p3, department=self.dept)
        with open(os.path.join(CUR_DIR, 'test_files', TEST_PDF_FILENAME), 'rb') as f:
            pdf_file = File(f, name=TEST_PDF_FILENAME)
            c2.thesis.document = pdf_file
            c2.thesis.title = 'test'
            c2.thesis.abstract = 'test abstract'
            c2.thesis.save()
            c2.thesis.keywords.add(Keyword.objects.create(text='test'))
            c2.committee_members.add(cm)
            c2.thesis.submit()
        self.assertEqual(len(Candidate.get_candidates_by_status('in_progress')), 1)
        self.assertEqual(Candidate.get_candidates_by_status('in_progress')[0].person.netid, 'tjones@brown.edu')
        self.assertEqual(Candidate.get_candidates_by_status('awaiting_gradschool')[0].person.netid, 'rsmith@brown.edu')

    def test_get_candidates_status_2(self):
        p = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid='rsmith@brown.edu', last_name='smith', email='r_smith@brown.edu')
        p3 = Person.objects.create(netid='bjohnson@brown.edu', last_name='johnson', email='bob_johnson@brown.edu')
        p4 = Person.objects.create(last_name='thomson')
        c = Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        c3 = Candidate.objects.create(person=p3, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        cm = CommitteeMember.objects.create(person=p4, department=self.dept)
        keyword = Keyword.objects.create(text='test')
        with open(os.path.join(CUR_DIR, 'test_files', TEST_PDF_FILENAME), 'rb') as f:
            pdf_file = File(f, name=TEST_PDF_FILENAME)
            for candidate in [c, c2, c3]:
                candidate.thesis.document = pdf_file
                candidate.thesis.title = 'test'
                candidate.thesis.abstract = 'test abstract'
                candidate.thesis.save()
                candidate.thesis.keywords.add(keyword)
                candidate.committee_members.add(cm)
                candidate.thesis.submit()
                if candidate.person.netid == 'tjones@brown.edu':
                    candidate.thesis.accept()
                elif candidate.person.netid == 'rsmith@brown.edu':
                    candidate.thesis.reject()
                elif candidate.person.netid == 'bjohnson@brown.edu':
                    candidate.thesis.accept()
                    complete_gradschool_checklist(candidate)
        paperwork_incomplete = Candidate.get_candidates_by_status('paperwork_incomplete')
        self.assertEqual(len(paperwork_incomplete), 1)
        self.assertEqual(paperwork_incomplete[0].person.netid, 'tjones@brown.edu')
        self.assertEqual(Candidate.get_candidates_by_status('dissertation_rejected')[0].person.netid, 'rsmith@brown.edu')
        complete = Candidate.get_candidates_by_status('complete')
        self.assertEqual(len(complete), 1)
        self.assertEqual(complete[0].person.netid, 'bjohnson@brown.edu')

    def test_candidates_by_status_sorted(self):
        p = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid='rsmith@brown.edu', last_name='Smith', email='r_smith@brown.edu')
        p3 = Person.objects.create(netid='bjohnson@brown.edu', last_name='Johnson', email='bob_johnson@brown.edu')
        c = Candidate.objects.create(person=p, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        c3 = Candidate.objects.create(person=p3, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        sorted_candidates = Candidate.get_candidates_by_status(status='all')
        self.assertEqual(sorted_candidates[0].person.last_name, 'Johnson')
        c.thesis.title = 'zzzz'
        c.thesis.save()
        c2.thesis.title = 'aaaa'
        c2.thesis.save()
        c3.thesis.title = 'hhhh'
        c3.thesis.save()
        sorted_candidates = Candidate.get_candidates_by_status(status='all', sort_param='title')
        self.assertEqual(sorted_candidates[0].thesis.title, 'aaaa')


class TestCommitteeMember(TestCase):

    def setUp(self):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D')
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME)

    def test_create_committee_member(self):
        cm = CommitteeMember.objects.create(person=self.person, department=self.dept)
        self.assertEqual(cm.person.last_name, LAST_NAME)
        self.assertEqual(cm.role, 'reader')
        self.assertEqual(cm.department.name, 'Engineering')

    def test_create_member_affiliation(self):
        cm = CommitteeMember.objects.create(person=self.person, affiliation='Providence College')
        self.assertEqual(cm.affiliation, 'Providence College')

    def test_affiliation_or_dept_required(self):
        with self.assertRaises(CommitteeMemberException):
            CommitteeMember.objects.create(person=self.person)
        with self.assertRaises(CommitteeMemberException):
            CommitteeMember.objects.create(person=self.person, affiliation='')


class TestKeyword(TestCase):

    def test_create_keyword(self):
        Keyword.objects.create(text='test', authority='fast', authority_uri='http://example.org/fast', value_uri='http://example.org/fast/1234')
        self.assertEqual(Keyword.objects.all()[0].text, 'test')
        self.assertEqual(Keyword.objects.all()[0].search_text, 'test')

    def test_empty_keyword(self):
        with self.assertRaises(KeywordException):
            Keyword.objects.create(text='')

    def test_keyword_text_normalized(self):
        Keyword.objects.create(text=COMPOSED_TEXT)
        self.assertEqual(Keyword.objects.all()[0].text, DECOMPOSED_TEXT)

    def test_keyword_invalid_chars_removed(self):
        Keyword.objects.create(text='test\x0c kw')
        self.assertEqual(Keyword.objects.all()[0].text, 'test kw')

    def test_keyword_too_long(self):
        kw_text = 'long' * 50
        with self.assertRaises(KeywordException):
            Keyword.objects.create(text=kw_text)

    def test_unique(self):
        Keyword.objects.create(text=COMPOSED_TEXT)
        with self.assertRaises(IntegrityError):
            Keyword.objects.create(text=DECOMPOSED_TEXT)

    def test_search_keywords_composed(self):
        k1 = Keyword.objects.create(text=COMPOSED_TEXT)
        self.assertEqual(k1.text, DECOMPOSED_TEXT)
        self.assertNotEqual(k1.text, COMPOSED_TEXT)
        results = Keyword.search(term=COMPOSED_TEXT)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, DECOMPOSED_TEXT)

    def test_search_order(self):
        k1 = Keyword.objects.create(text='zebra')
        k2 = Keyword.objects.create(text='aardvark')
        results = Keyword.search(term='r', order='text')
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, k2.id)


def add_file_to_thesis(thesis):
    with open(os.path.join(CUR_DIR, 'test_files', TEST_PDF_FILENAME), 'rb') as f:
        pdf_file = File(f, name=TEST_PDF_FILENAME)
        thesis.document = pdf_file
        thesis.save()


def add_metadata_to_thesis(thesis):
    thesis.title = 'test'
    thesis.abstract = 'test abstract'
    keyword = Keyword.objects.create(text='keyword')
    thesis.keywords.add(keyword)
    thesis.save()


class TestThesis(TestCase):

    def setUp(self):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor of Philosophy')
        self.person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        self.cm_person = Person.objects.create(netid='rsmith@brown.edu', last_name='Smith', email='r_smith@brown.edu')
        self.candidate = Candidate.objects.create(person=self.person, year=CURRENT_YEAR, department=self.dept, degree=self.degree)
        self.committee_member = CommitteeMember.objects.create(person=self.cm_person, department=self.dept)

    def test_pid_unique(self):
        self.candidate.thesis.pid = '1234'
        self.candidate.thesis.save()
        candidate2 = Candidate.objects.create(person=self.person, year=2018, department=self.dept, degree=self.degree)
        with self.assertRaises(IntegrityError) as cm:
            candidate2.thesis.pid = '1234'
            candidate2.thesis.save()
        self.assertTrue('pid' in str(cm.exception))

    def test_multiple_theses_with_no_pid(self):
        candidate2 = Candidate.objects.create(person=self.person, year=2018, department=self.dept, degree=self.degree)
        candidate2.thesis.pid = ''
        candidate2.thesis.save()
        self.assertEqual(candidate2.thesis.pid, None)

    def test_thesis_create_format_checklist(self):
        self.assertEqual(self.candidate.thesis.format_checklist.title_page_comment, '')

    def test_thesis_create_language(self):
        self.assertEqual(self.candidate.thesis.language.code, 'eng')

    def test_clean_user_text(self):
        self.candidate.thesis.abstract = 'test<br /> string'
        self.candidate.thesis.save()
        self.assertEqual(self.candidate.thesis.abstract, 'test string')
        self.candidate.thesis.abstract = 'test<br> string'
        self.candidate.thesis.save()
        self.assertEqual(self.candidate.thesis.abstract, 'test string')
        self.candidate.thesis.title = 'test\x0c string'
        self.candidate.thesis.save()
        self.assertEqual(self.candidate.thesis.title, 'test string')

    def test_thesis_label(self):
        #could be "Thesis" or "Dissertation", depending on degree type
        self.assertEqual(self.candidate.thesis.label, 'Dissertation')
        degree2 = Degree.objects.create(abbreviation='MS', name='Masters', degree_type='masters')
        self.candidate.degree = degree2
        self.candidate.save()
        self.assertEqual(self.candidate.thesis.label, 'Thesis')

    def test_add_file_to_thesis(self):
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        self.assertEqual(thesis.original_file_name, TEST_PDF_FILENAME)
        self.assertTrue(thesis.current_file_name.startswith(TEST_PDF_FILENAME.split(u'.')[0]))
        self.assertTrue(thesis.current_file_name.endswith('.pdf'))
        self.assertEqual(thesis.checksum, 'b1938fc5549d1b5b42c0b695baa76d5df5f81ac3')
        self.assertEqual(thesis.status, Thesis.STATUS_CHOICES.not_submitted)

    def test_invalid_file(self):
        with open(os.path.join(CUR_DIR, 'test_files', 'test_obj'), 'rb') as f:
            bad_file = File(f, name='test_obj')
            with self.assertRaises(ThesisException):
                self.candidate.thesis.document = bad_file
                self.candidate.thesis.save()

    def test_submit(self):
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.assertTrue(thesis.ready_to_submit())
        thesis.submit()
        self.assertEqual(thesis.status, Thesis.STATUS_CHOICES.pending)
        self.assertEqual(thesis.date_submitted.date(), timezone.now().date())
        self.assertEqual(len(mail.outbox), 1)

    def test_submit_check_document(self):
        self.candidate.committee_members.add(self.committee_member)
        add_metadata_to_thesis(self.candidate.thesis)
        self.assertFalse(self.candidate.thesis.ready_to_submit())
        with self.assertRaises(ThesisException) as cm:
            self.candidate.thesis.submit()
        self.assertTrue('no document has been uploaded' in str(cm.exception))

    def test_submit_check_metadata(self):
        add_file_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.assertFalse(self.candidate.thesis.ready_to_submit())
        with self.assertRaises(ThesisException) as cm:
            Thesis.objects.all()[0].submit()
        self.assertTrue('metadata incomplete' in str(cm.exception))

    def test_submit_check_committee_member(self):
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.assertFalse(self.candidate.thesis.ready_to_submit())
        with self.assertRaises(ThesisException) as cm:
            Thesis.objects.all()[0].submit()
        self.assertTrue('no committee members' in str(cm.exception))

    def test_submit_check_state(self):
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.status = Thesis.STATUS_CHOICES.pending
        self.candidate.thesis.save()
        self.assertFalse(self.candidate.thesis.ready_to_submit())
        with self.assertRaises(ThesisException) as cm:
            self.candidate.thesis.submit()
        self.assertTrue('can\'t submit thesis: wrong status' in str(cm.exception), str(cm.exception))

    def test_accept_and_lock(self):
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        self.candidate.committee_members.add(self.committee_member)
        thesis.submit()
        self.assertTrue(thesis.is_locked())
        thesis.accept()
        self.assertEqual(thesis.status, Thesis.STATUS_CHOICES.accepted)
        self.assertTrue(thesis.is_locked())
        self.assertEqual(len(mail.outbox), 2) #one submit email, one accept email
        thesis.mark_ingested('1234')
        self.assertTrue(thesis.is_locked())

    def test_accept_check(self):
        with self.assertRaises(ThesisException):
            self.candidate.thesis.accept()

    def test_reject(self):
        thesis = self.candidate.thesis
        add_file_to_thesis(thesis)
        add_metadata_to_thesis(thesis)
        self.candidate.committee_members.add(self.committee_member)
        thesis.submit()
        Candidate.objects.all()[0].thesis.reject()
        self.assertEqual(len(mail.outbox), 2) #one submit email, one reject email
        self.assertEqual(Candidate.objects.all()[0].thesis.status, Thesis.STATUS_CHOICES.rejected)

    def test_reject_check(self):
        with self.assertRaises(ThesisException):
            self.candidate.thesis.reject()

    def test_mark_ingested(self):
        thesis = self.candidate.thesis
        thesis.mark_ingested('1234')
        thesis = Thesis.objects.all()[0]
        self.assertEqual(thesis.pid, '1234')

    def test_mark_ingest_error(self):
        thesis = self.candidate.thesis
        thesis.mark_ingest_error()
        thesis = Thesis.objects.all()[0]
        self.assertEqual(thesis.status, Thesis.STATUS_CHOICES.ingest_error)

    def test_ready_to_ingest(self):
        self.assertFalse(self.candidate.thesis.ready_to_ingest())
        self.candidate.thesis.status = Thesis.STATUS_CHOICES.accepted
        self.candidate.thesis.save()
        self.assertFalse(self.candidate.thesis.ready_to_ingest())
        complete_gradschool_checklist(self.candidate)
        self.assertTrue(self.candidate.thesis.ready_to_ingest())
        self.candidate.year += 1
        self.candidate.save()
        self.assertFalse(self.candidate.thesis.ready_to_ingest())

    def test_open_for_reupload(self):
        with self.assertRaises(ThesisException) as cm:
            self.candidate.thesis.open_for_reupload()

    def test_accept_then_open_for_reupload(self):
        add_file_to_thesis(self.candidate.thesis)
        add_metadata_to_thesis(self.candidate.thesis)
        self.candidate.committee_members.add(self.committee_member)
        self.candidate.thesis.submit()
        self.candidate.thesis.accept()
        complete_gradschool_checklist(self.candidate)
        self.candidate.thesis.open_for_reupload()
        self.assertEqual(self.candidate.thesis.status, Thesis.STATUS_CHOICES.not_submitted)
        self.assertFalse(self.candidate.thesis.is_locked())
        self.assertTrue(self.candidate.gradschool_checklist.bursar_receipt)

