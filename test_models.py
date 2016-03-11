# -*- coding: utf-8 -*-
from datetime import date
import os
from django.core.files import File
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from .models import (
        Person,
        DuplicateNetidException,
        DuplicateOrcidException,
        DuplicateEmailException,
        Year,
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


COMPOSED_TEXT = u'tëst'
DECOMPOSED_TEXT = u'tëst'


class TestPerson(TestCase):

    def test_person_create(self):
        netid = u'tjones@brown.edu'
        last_name = u'jones'
        first_name = u'tom'
        Person.objects.create(netid=netid, last_name=last_name, first_name=first_name)
        self.assertEqual(Person.objects.all()[0].netid, netid)
        self.assertEqual(Person.objects.all()[0].last_name, last_name)
        self.assertEqual(Person.objects.all()[0].first_name, first_name)

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


class TestYear(TestCase):

    def test_year(self):
        Year.objects.create(year=u'2016')
        self.assertEqual(Year.objects.all()[0].year, u'2016')

    def test_unique(self):
        Year.objects.create(year=u'2016')
        with self.assertRaises(IntegrityError):
            Year.objects.create(year=u'2016')


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

    def test_create(self):
        Degree.objects.create(abbreviation=u'Ph.D.', name=u'Doctor of Philosophy')
        self.assertEqual(Degree.objects.all()[0].abbreviation, u'Ph.D.')
        self.assertEqual(Degree.objects.all()[0].name, u'Doctor of Philosophy')

    def test_unique_abbr(self):
        Degree.objects.create(abbreviation=u'Ph.D.', name=u'Doctor of Philosophy')
        with self.assertRaises(IntegrityError):
            Degree.objects.create(abbreviation=u'Ph.D.', name=u'Doctor of Philosophy 2')

    def test_unique_name(self):
        Degree.objects.create(abbreviation=u'Ph.D.', name=u'Doctor of Philosophy')
        with self.assertRaises(IntegrityError):
            Degree.objects.create(abbreviation=u'Ph.D. 2', name=u'Doctor of Philosophy')


class TestCandidate(TestCase):

    def setUp(self):
        self.year = Year.objects.create(year=u'2016')
        self.dept = Department.objects.create(name=u'Engineering')
        self.degree = Degree.objects.create(abbreviation=u'Ph.D')
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))

    def test_person_must_have_netid(self):
        #if a person is becoming a candidate, they must have a Brown netid
        p = Person.objects.create(last_name=u'jones')
        with self.assertRaises(CandidateException) as cm:
            Candidate.objects.create(person=p, year=self.year, department=self.dept, degree=self.degree)
        self.assertEqual(cm.exception.message, u'candidate must have a Brown netid')

    def test_create_candidate(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=u'jones')
        p2 = Person.objects.create(netid=u'rsmith@brown.edu', last_name=u'smith')
        Candidate.objects.create(person=p, year=self.year, department=self.dept, degree=self.degree)
        candidate = Candidate.objects.all()[0]
        self.assertEqual(candidate.person.netid, u'tjones@brown.edu')
        self.assertEqual(candidate.date_registered, date.today())
        self.assertEqual(candidate.thesis.status, 'not_submitted')
        self.assertEqual(candidate.gradschool_checklist.dissertation_fee, None)
        candidate.committee_members.add(CommitteeMember.objects.create(person=p2, department=self.dept))
        self.assertEqual(Candidate.objects.all()[0].committee_members.all()[0].person.last_name, 'smith')

    def test_get_candidates_all(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=u'jones')
        p2 = Person.objects.create(netid=u'rjones@brown.edu', last_name=u'jones')
        Candidate.objects.create(person=p, year=self.year, department=self.dept, degree=self.degree)
        Candidate.objects.create(person=p2, year=self.year, department=self.dept, degree=self.degree)
        self.assertEqual(len(Candidate.get_candidates_by_status('all')), 2)

    def test_get_candidates_status(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=u'jones')
        p2 = Person.objects.create(netid=u'rsmith@brown.edu', last_name=u'smith')
        c = Candidate.objects.create(person=p, year=self.year, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=self.year, department=self.dept, degree=self.degree)
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            c2.thesis = Thesis.objects.create(document=pdf_file, title=u'test', abstract=u'test abstract')
            c2.thesis.keywords.add(Keyword.objects.create(text=u'test'))
            c2.save()
            c2.thesis.submit()
        self.assertEqual(len(Candidate.get_candidates_by_status('in_progress')), 1)
        self.assertEqual(Candidate.get_candidates_by_status('in_progress')[0].person.netid, 'tjones@brown.edu')
        self.assertEqual(Candidate.get_candidates_by_status('awaiting_gradschool')[0].person.netid, 'rsmith@brown.edu')

    def test_get_candidates_status_2(self):
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=u'jones')
        p2 = Person.objects.create(netid=u'rsmith@brown.edu', last_name=u'smith')
        p3 = Person.objects.create(netid=u'bjohnson@brown.edu', last_name=u'johnson')
        c = Candidate.objects.create(person=p, year=self.year, department=self.dept, degree=self.degree)
        c2 = Candidate.objects.create(person=p2, year=self.year, department=self.dept, degree=self.degree)
        c3 = Candidate.objects.create(person=p3, year=self.year, department=self.dept, degree=self.degree)
        keyword = Keyword.objects.create(text=u'test')
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            for candidate in [c, c2, c3]:
                candidate.thesis = Thesis.objects.create(document=pdf_file, title=u'test', abstract=u'test abstract')
                candidate.thesis.keywords.add(keyword)
                candidate.save()
                candidate.thesis.submit()
        Candidate.objects.filter(person__netid='tjones@brown.edu')[0].thesis.accept()
        Candidate.objects.filter(person__netid='rsmith@brown.edu')[0].thesis.reject()
        johnson = Candidate.objects.filter(person__netid='bjohnson@brown.edu')[0]
        johnson.thesis.accept()
        johnson.gradschool_checklist.dissertation_fee = timezone.now()
        johnson.gradschool_checklist.bursar_receipt = timezone.now()
        johnson.gradschool_checklist.gradschool_exit_survey = timezone.now()
        johnson.gradschool_checklist.earned_docs_survey = timezone.now()
        johnson.gradschool_checklist.pages_submitted_to_gradschool = timezone.now()
        johnson.gradschool_checklist.save()
        paperwork_incomplete = Candidate.get_candidates_by_status('paperwork_incomplete')
        self.assertEqual(len(paperwork_incomplete), 1)
        self.assertEqual(paperwork_incomplete[0].person.netid, 'tjones@brown.edu')
        self.assertEqual(Candidate.get_candidates_by_status('dissertation_rejected')[0].person.netid, 'rsmith@brown.edu')
        complete = Candidate.get_candidates_by_status('complete')
        self.assertEqual(len(complete), 1)
        self.assertEqual(complete[0].person.netid, 'bjohnson@brown.edu')


class TestCommitteeMember(TestCase):

    def setUp(self):
        self.year = Year.objects.create(year=u'2016')
        self.dept = Department.objects.create(name=u'Engineering')
        self.degree = Degree.objects.create(abbreviation=u'Ph.D')
        self.person = Person.objects.create(netid=u'tjones@brown.edu', last_name=u'jonês')

    def test_create_committee_member(self):
        cm = CommitteeMember.objects.create(person=self.person, department=self.dept)
        self.assertEqual(cm.person.last_name, u'jonês')
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
        self.language = Language.objects.create(code=u'eng', name=u'English')
        self.keyword = Keyword.objects.create(text=u'keyword')
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))

    def test_create_thesis(self):
        '''test thesis creation; ignore any interaction with Candidate'''
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis = Thesis.objects.create(document=pdf_file, language=self.language)
        self.assertEqual(thesis.file_name, 'test.pdf')
        self.assertEqual(thesis.checksum, 'b1938fc5549d1b5b42c0b695baa76d5df5f81ac3')
        self.assertEqual(thesis.language.name, u'English')
        self.assertEqual(thesis.status, u'not_submitted')

    def test_thesis_without_file(self):
        #allow creating thesis without the actual file - if user wants to start adding metadata before the file
        Thesis.objects.create()
        self.assertEqual(len(Thesis.objects.all()), 1)

    def test_invalid_file(self):
        with open(os.path.join(self.cur_dir, 'test_files', 'test_obj'), 'rb') as f:
            bad_file = File(f)
            with self.assertRaises(ThesisException):
                Thesis.objects.create(document=bad_file)

    def test_submit(self):
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis = Thesis.objects.create(document=pdf_file, title=u'test', abstract=u'test abstract',
                                           language=self.language)
        thesis.keywords.add(self.keyword)
        thesis.submit()
        thesis = Thesis.objects.all()[0] #reload thesis data
        self.assertEqual(thesis.status, 'pending')
        self.assertEqual(thesis.date_submitted.date(), timezone.now().date())

    def test_submit_check(self):
        thesis = Thesis.objects.create()
        with self.assertRaises(ThesisException) as cm:
            thesis.submit()
        self.assertTrue('no document has been uploaded' in cm.exception.message)
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis.document = pdf_file
            thesis.save()
        with self.assertRaises(ThesisException) as cm:
            Thesis.objects.all()[0].submit()
        self.assertTrue('metadata incomplete' in cm.exception.message)

    def test_accept(self):
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis = Thesis.objects.create(document=pdf_file, title=u'test', abstract=u'test abstract',
                                           language=self.language)
        thesis.keywords.add(self.keyword)
        thesis.submit()
        thesis = Thesis.objects.all()[0] #reload thesis data
        thesis.accept()
        thesis = Thesis.objects.all()[0] #reload thesis data
        self.assertEqual(thesis.status, 'accepted')

    def test_accept_check(self):
        thesis = Thesis.objects.create()
        with self.assertRaises(ThesisException):
            thesis.accept()

    def test_reject(self):
        with open(os.path.join(self.cur_dir, 'test_files', 'test.pdf'), 'rb') as f:
            pdf_file = File(f)
            thesis = Thesis.objects.create(document=pdf_file, title=u'test', abstract=u'test abstract',
                                           language=self.language)
        thesis.keywords.add(self.keyword)
        thesis.submit()
        thesis = Thesis.objects.all()[0] #reload thesis data
        thesis.reject()
        thesis = Thesis.objects.all()[0] #reload thesis data
        self.assertEqual(thesis.status, 'rejected')

    def test_reject_check(self):
        thesis = Thesis.objects.create()
        with self.assertRaises(ThesisException):
            thesis.reject()
