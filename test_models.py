# -*- coding: utf-8 -*-
from django.db import IntegrityError
from django.test import TestCase
from .models import Person


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
