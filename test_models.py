# -*- coding: utf-8 -*-
from django.db import IntegrityError
from django.test import TestCase
from .models import Person, Year, Department, Degree


class TestPeople(TestCase):

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
        with self.assertRaises(IntegrityError):
            Person.objects.create(netid=netid)

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
