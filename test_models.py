# -*- coding: utf-8 -*-
from datetime import date
import os
from django.core.files import File
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from .models import (
        Person,
        DuplicateNetidException,
        DuplicateOrcidException,
        DuplicateEmailException,
        Department,
        Degree,
        CandidateException,
        Candidate,
        GradschoolChecklist,
        CommitteeMemberException,
        CommitteeMember,
        Language,
        KeywordException,
        Keyword,
        ThesisException,
        Thesis,
    )


LAST_NAME = u'Jonës'
FIRST_NAME = u'T©m'
COMPOSED_TEXT = u'tëst'
DECOMPOSED_TEXT = u'tëst'


class TestPerson(TestCase):

    def test_person_create(self):
        netid = u'tjones@brown.edu'
        Person.objects.create(netid=netid, last_name=LAST_NAME, first_name=FIRST_NAME)
        self.assertEqual(Person.objects.all()[0].netid, netid)
        self.assertEqual(Person.objects.all()[0].last_name, LAST_NAME)
        self.assertEqual(Person.objects.all()[0].first_name, FIRST_NAME)

    def test_netid_optional(self):
        p = Person.objects.create()
        self.assertEqual(Person.objects.all()[0].netid, None)

    def test_netid_unique(self):
        netid = u'tjones@brown.edu'
        Person.objects.create(netid=netid)
        with self.assertRaises(DuplicateNetidException):
            Person.objects.create(netid=netid)

    def test_orcid_unique(self):
        orcid = u'0000-0002-5286-384X'
        Person.objects.create(orcid=orcid)
        with self.assertRaises(DuplicateOrcidException):
            Person.objects.create(orcid=orcid)

    def test_email_unique(self):
        email = u'tom_jones@brown.edu'
        Person.objects.create(email=email)
        with self.assertRaises(DuplicateEmailException):
            Person.objects.create(email=email)

    def test_netid_allow_multiple_blank(self):
        Person.objects.create()
        Person.objects.create()
        self.assertEqual(Person.objects.all()[0].netid, None)
        self.assertEqual(Person.objects.all()[1].netid, None)

    def test_utf8mb4_char_in_name(self):
        last_name = u'last𝌆name'
        Person.objects.create(last_name=last_name)
        self.assertEqual(Person.objects.all()[0].last_name, last_name)


class TestDepartment(TestCase):

    def test_create(self):
        Department.objects.create(name=u'tëst dept')
        self.assertEqual(Department.objects.all()[0].name, u'tëst dept')

    def test_unique(self):
        name = u'tëst dept'
        Department.objects.create(name=name)
        with self.assertRaises(IntegrityError):
            Department.objects.create(name=name)


class TestDegree(TestCase):

    def setUp(self):
        Degree.objects.create(abbreviation=u'Ph.D.', name=u'Doctor of Philosophy')

    def test_create(self):
        self.assertEqual(Degree.objects.all()[0].abbreviation, u'Ph.D.')
        self.assertEqual(Degree.objects.all()[0].name, u'Doctor of Philosophy')

    def test_unique_abbr(self):
        with self.assertRaises(IntegrityError):
            Degree.objects.create(abbreviation=u'Ph.D.', name=u'Doctor of Philosophy 2')

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            Degree.objects.create(abbreviation=u'Ph.D. 2', name=u'Doctor of Philosophy')


class TestCandidate(TransactionTestCase):

    def setUp(self):
        self.dept = Department.objects.create(name=u'Engineering')
        self.degree = Degree.objects.create(abbreviation=u'Ph.D')
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))

    def test_person_must_have_netid(self):
        #if a person is becoming a candidate, they must have a Brown netid
        p = Person.objects.create(last_name=LAST_NAME)
        with self.assertRaises(CandidateException) as cm:
            Candidate.objects.create(person=p, year=2016, department=self.dept, degree=self.degree)
        self.assertEqual(cm.exception.message, u'candidate must have a Brown netid')

    def test_create_candidate(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid=u'rsmith@brown.edu', last_name=u'smith')
        Candidate.objects.create(person=p, year=2016, department=self.dept, degree=self.degree)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.person.netid, u'tjones@brown.edu')
        self.assertEqual(candidate.date_registered, date.today())
        self.assertEqual(candidate.thesis.status, 'not_submitted')
        self.assertEqual(candidate.gradschool_checklist.dissertation_fee, None)
        candidate.committee_members.add(CommitteeMember.objects.create(person=p2, department=self.dept))
        self.assertEqual(Candidate.objects.all()[0].committee_members.all()[0].person.last_name, 'smith')

    def test_year_validation(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        with self.assertRaises(Exception):
            Candidate.objects.create(person=p, year='abc', department=self.dept, degree=self.degree)

    def test_get_candidates_all(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid=u'rjones@brown.edu', last_name=u'jones', email='r_jones@brown.edu')
        Candidate.objects.create(person=p, year=2016, department=self.dept, degree=self.degree)
        Candidate.objects.create(person=p2, year=2016, department=self.dept, degree=self.degree)
        self.assertEqual(len(Candidate.get_candidates_by_status('all')), 2)

    def test_get_candidates_status(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid=u'rsmith@brown.edu', last_name=u'smith', email='r_smith@brown.edu')
        c = Candidate.objects.create(person=p, year=2016, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=2016, department=self.dept, degree=self.degree)
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            c2.thesis.document = pdf_file
            c2.thesis.title = u'test'
            c2.thesis.abstract = u'test abstract'
            c2.thesis.save()
            c2.thesis.keywords.add(Keyword.objects.create(text=u'test'))
            c2.thesis.submit()
        self.assertEqual(len(Candidate.get_candidates_by_status('in_progress')), 1)
        self.assertEqual(Candidate.get_candidates_by_status('in_progress')[0].person.netid, 'tjones@brown.edu')
        self.assertEqual(Candidate.get_candidates_by_status('awaiting_gradschool')[0].person.netid, 'rsmith@brown.edu')

    def test_get_candidates_status_2(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid=u'rsmith@brown.edu', last_name=u'smith', email='r_smith@brown.edu')
        p3 = Person.objects.create(netid=u'bjohnson@brown.edu', last_name=u'johnson', email='bob_johnson@brown.edu')
        c = Candidate.objects.create(person=p, year=2016, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=2016, department=self.dept, degree=self.degree)
        c3 = Candidate.objects.create(person=p3, year=2016, department=self.dept, degree=self.degree)
        keyword = Keyword.objects.create(text=u'test')
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            for candidate in [c, c2, c3]:
                candidate.thesis.document = pdf_file
                candidate.thesis.title = u'test'
                candidate.thesis.abstract = u'test abstract'
                candidate.thesis.save()
                candidate.thesis.keywords.add(keyword)
                candidate.thesis.submit()
                if candidate.person.netid == 'tjones@brown.edu':
                    candidate.thesis.accept()
                elif candidate.person.netid == 'rsmith@brown.edu':
                    candidate.thesis.reject()
                elif candidate.person.netid == 'bjohnson@brown.edu':
                    candidate.thesis.accept()
                    candidate.gradschool_checklist.dissertation_fee = timezone.now()
                    candidate.gradschool_checklist.bursar_receipt = timezone.now()
                    candidate.gradschool_checklist.gradschool_exit_survey = timezone.now()
                    candidate.gradschool_checklist.earned_docs_survey = timezone.now()
                    candidate.gradschool_checklist.pages_submitted_to_gradschool = timezone.now()
                    candidate.gradschool_checklist.save()
        paperwork_incomplete = Candidate.get_candidates_by_status('paperwork_incomplete')
        self.assertEqual(len(paperwork_incomplete), 1)
        self.assertEqual(paperwork_incomplete[0].person.netid, 'tjones@brown.edu')
        self.assertEqual(Candidate.get_candidates_by_status('dissertation_rejected')[0].person.netid, 'rsmith@brown.edu')
        complete = Candidate.get_candidates_by_status('complete')
        self.assertEqual(len(complete), 1)
        self.assertEqual(complete[0].person.netid, 'bjohnson@brown.edu')

    def test_candidates_by_status_sorted(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        p2 = Person.objects.create(netid=u'rsmith@brown.edu', last_name=u'Smith', email='r_smith@brown.edu')
        p3 = Person.objects.create(netid=u'bjohnson@brown.edu', last_name=u'Johnson', email='bob_johnson@brown.edu')
        c = Candidate.objects.create(person=p, year=2016, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=2016, department=self.dept, degree=self.degree)
        c3 = Candidate.objects.create(person=p3, year=2016, department=self.dept, degree=self.degree)
        sorted_candidates = Candidate.get_candidates_by_status(status='all')
        self.assertEqual(sorted_candidates[0].person.last_name, u'Johnson')
        c.thesis.title = u'zzzz'
        c.thesis.save()
        c2.thesis.title = u'aaaa'
        c2.thesis.save()
        c3.thesis.title = u'hhhh'
        c3.thesis.save()
        sorted_candidates = Candidate.get_candidates_by_status(status='all', sort_param='title')
        self.assertEqual(sorted_candidates[0].thesis.title, u'aaaa')


class TestCommitteeMember(TestCase):

    def setUp(self):
        self.dept = Department.objects.create(name=u'Engineering')
        self.degree = Degree.objects.create(abbreviation=u'Ph.D')
        self.person = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME)

    def test_create_committee_member(self):
        cm = CommitteeMember.objects.create(person=self.person, department=self.dept)
        self.assertEqual(cm.person.last_name, LAST_NAME)
        self.assertEqual(cm.role, u'reader')
        self.assertEqual(cm.department.name, u'Engineering')

    def test_create_member_affiliation(self):
        cm = CommitteeMember.objects.create(person=self.person, affiliation='Providence College')
        self.assertEqual(cm.affiliation, u'Providence College')

    def test_affiliation_or_dept_required(self):
        with self.assertRaises(CommitteeMemberException):
            CommitteeMember.objects.create(person=self.person)
        with self.assertRaises(CommitteeMemberException):
            CommitteeMember.objects.create(person=self.person, affiliation='')


class TestKeyword(TestCase):

    def test_create_keyword(self):
        Keyword.objects.create(text=u'test', authority=u'fast', authority_uri=u'http://example.org/fast', value_uri=u'http://example.org/fast/1234')
        self.assertEqual(Keyword.objects.all()[0].text, u'test')
        self.assertEqual(Keyword.objects.all()[0].search_text, u'test')

    def test_empty_keyword(self):
        with self.assertRaises(KeywordException):
            Keyword.objects.create(text=u'')

    def test_keyword_text_normalized(self):
        Keyword.objects.create(text=COMPOSED_TEXT)
        self.assertEqual(Keyword.objects.all()[0].text, DECOMPOSED_TEXT)

    def test_keyword_too_long(self):
        kw_text = u'long' * 50
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
        k1 = Keyword.objects.create(text=u'zebra')
        k2 = Keyword.objects.create(text=u'aardvark')
        results = Keyword.search(term=u'r', order='text')
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, k2.id)


class TestThesis(TestCase):

    def setUp(self):
        self.dept = Department.objects.create(name='Engineering')
        self.degree = Degree.objects.create(abbreviation='Ph.D', name='Doctor of Philosophy')
        self.language = Language.objects.create(code=u'eng', name=u'English')
        self.keyword = Keyword.objects.create(text=u'keyword')
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.person = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, email='tom_jones@brown.edu')
        self.candidate = Candidate.objects.create(person=self.person, year=2016, department=self.dept, degree=self.degree)

    def test_thesis_create_format_checklist(self):
        self.assertEqual(self.candidate.thesis.format_checklist.title_page_comment, u'')

    def test_add_file_to_thesis(self):
        thesis = self.candidate.thesis
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis.document = pdf_file
            thesis.save()
        self.assertEqual(thesis.file_name, 'test.pdf')
        self.assertEqual(thesis.checksum, 'b1938fc5549d1b5b42c0b695baa76d5df5f81ac3')
        self.assertEqual(thesis.status, u'not_submitted')

    def test_invalid_file(self):
        with open(os.path.join(self.cur_dir, 'test_files', 'test_obj'), 'rb') as f:
            bad_file = File(f)
            with self.assertRaises(ThesisException):
                self.candidate.thesis.document = bad_file
                self.candidate.thesis.save()

    def test_submit(self):
        thesis = self.candidate.thesis
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis.document = pdf_file
            thesis.title = u'test'
            thesis.abstract = u'test abstract'
            thesis.save()
        thesis.keywords.add(self.keyword)
        thesis.submit()
        self.assertEqual(thesis.status, 'pending')
        self.assertEqual(thesis.date_submitted.date(), timezone.now().date())

    def test_submit_check(self):
        with self.assertRaises(ThesisException) as cm:
            self.candidate.thesis.submit()
        self.assertTrue('no document has been uploaded' in cm.exception.message)
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            self.candidate.thesis.document = pdf_file
            self.candidate.thesis.save()
        with self.assertRaises(ThesisException) as cm:
            Thesis.objects.all()[0].submit()
        self.assertTrue('metadata incomplete' in cm.exception.message)

    def test_accept(self):
        thesis = self.candidate.thesis
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis.document = pdf_file
            thesis.title = u'test'
            thesis.abstract = u'test abstract'
            thesis.language = self.language
            thesis.save()
        thesis.keywords.add(self.keyword)
        thesis.submit()
        Candidate.objects.all()[0].thesis.accept()
        self.assertEqual(Candidate.objects.all()[0].thesis.status, 'accepted')

    def test_accept_check(self):
        with self.assertRaises(ThesisException):
            self.candidate.thesis.accept()

    def test_reject(self):
        thesis = self.candidate.thesis
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis.document = pdf_file
            thesis.title = u'test'
            thesis.abstract = u'test abstract'
            thesis.language = self.language
            thesis.save()
        thesis.keywords.add(self.keyword)
        thesis.submit()
        Candidate.objects.all()[0].thesis.reject()
        self.assertEqual(Candidate.objects.all()[0].thesis.status, 'rejected')

    def test_reject_check(self):
        with self.assertRaises(ThesisException):
            self.candidate.thesis.reject()
