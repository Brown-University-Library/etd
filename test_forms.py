# -*- coding: utf-8 -*-
from django.test import TestCase
from .forms import RegistrationForm
from .models import Person, Candidate, Degree, Department, Year
from .test_views import FIRST_NAME, LAST_NAME


class TestRegistrationForm(TestCase):

    def setUp(self):
        self.person_data = {u'netid': u'wrongid@brown.edu', u'last_name': LAST_NAME, u'first_name': FIRST_NAME,
                u'address_street': u'123 Some Rd.', u'address_city': u'Ville',
                u'address_state': u'RI', u'address_zip': u'12345-5423',
                u'email': u'tomjones@brown.edu', u'phone': u'401-123-1234'}
        self.year = Year.objects.create(year=u'2016')
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
