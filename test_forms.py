# -*- coding: utf-8 -*-
from django.test import TestCase
from .forms import RegistrationForm
from .models import Person, Candidate, Degree, Department, Year
from .test_views import FIRST_NAME, LAST_NAME


class TestRegistrationForm(TestCase):

    def setUp(self):
        self.person_data = {u'netid': u'tjones@brown.edu', u'orcid': u'1234567890',
                u'last_name': LAST_NAME, u'first_name': FIRST_NAME,
                u'address_street': u'123 Some Rd.', u'address_city': u'Ville',
                u'address_state': u'RI', u'address_zip': u'12345-5423',
                u'email': u'tomjones@brown.edu', u'phone': u'401-123-1234'}
        self.year = Year.objects.create(year=u'2016')
        self.year2 = Year.objects.create(year=u'2017')
        self.dept = Department.objects.create(name=u'Engineering')
        self.degree = Degree.objects.create(abbreviation=u'Ph.D', name=u'Doctor')

    def test_clean_embargo(self):
        data = self.person_data.copy()
        data.update({u'year': self.year.id, u'department': self.dept.id, u'degree': self.degree.id,
                     u'set_embargo': 'on'})
        form = RegistrationForm(data)
        form.is_valid() #calls clean & does validation
        self.assertTrue(u'set_embargo' not in form.cleaned_data)
        self.assertEqual(form.cleaned_data['embargo_end_year'], u'2018')

    def test_clean_no_embargo(self):
        data = self.person_data.copy()
        data.update({u'year': self.year.id, u'department': self.dept.id, u'degree': self.degree.id})
        form = RegistrationForm(data)
        form.is_valid() #calls clean & does validation
        self.assertTrue(u'set_embargo' not in form.cleaned_data)
        self.assertTrue(u'embargo_end_year' not in form.cleaned_data)

    def test_handle_registration(self):
        data = self.person_data.copy()
        data.update({u'year': self.year.id, u'department': self.dept.id, u'degree': self.degree.id})
        form = RegistrationForm(data)
        form.is_valid()
        form.handle_registration()
        self.assertEqual(Person.objects.all()[0].last_name, LAST_NAME)
        self.assertEqual(Candidate.objects.all()[0].person.last_name, LAST_NAME)

    def test_registration_person_already_exists(self):
        person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, first_name=FIRST_NAME)
        data = self.person_data.copy()
        data[u'last_name'] = u'new last name'
        data.update({u'year': self.year.id, u'department': self.dept.id, u'degree': self.degree.id})
        form = RegistrationForm(data)
        form.is_valid()
        form.handle_registration()
        self.assertEqual(len(Person.objects.all()), 1)
        self.assertEqual(Person.objects.all()[0].last_name, u'new last name')

    def test_registration_orcid_already_exists(self):
        person = Person.objects.create(orcid='1234567890', last_name=LAST_NAME, first_name=FIRST_NAME)
        data = self.person_data.copy()
        data.update({u'year': self.year.id, u'department': self.dept.id, u'degree': self.degree.id})
        form = RegistrationForm(data)
        form.is_valid()
        form.handle_registration()
        self.assertEqual(len(Person.objects.all()), 1)

    def test_registration_edit_candidate_info(self):
        person = Person.objects.create(netid='tjones@brown.edu', last_name=LAST_NAME, first_name=FIRST_NAME)
        candidate = Candidate.objects.create(person=person, year=self.year, department=self.dept, degree=self.degree)
        data = self.person_data.copy()
        data.update({u'year': self.year2.id, u'department': self.dept.id, u'degree': self.degree.id})
        form = RegistrationForm(data)
        form.is_valid()
        form.handle_registration()
        self.assertEqual(len(Candidate.objects.all()), 1)
