# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import SimpleTestCase, TestCase
from .test_client import ETDTestClient
from .models import Person, Candidate, Year, Department, Degree


def get_auth_client():
    user = User.objects.create_user('test_user', 'pw')
    auth_client = ETDTestClient()
    auth_client.force_login(user)
    return auth_client


class TestStaticViews(SimpleTestCase):

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, u'<title>Electronic Theses & Dissertations at Brown University')
        self.assertContains(response, u'Ph.D. candidates at Brown must file their dissertations electronically.')

    def test_overview(self):
        response = self.client.get(reverse('overview'))
        self.assertContains(response, u'ETD Submission Overview')

    def test_faq(self):
        response = self.client.get(reverse('faq'))
        self.assertContains(response, u'Where are Brown’s ETDs available?')

    def test_tutorials(self):
        response = self.client.get(reverse('tutorials'))
        self.assertContains(response, u'Online Tutorials')

    def test_copyright(self):
        response = self.client.get(reverse('copyright'))
        self.assertContains(response, u'You own the copyright to your dissertation')


class TestRegister(TestCase):

    def test_register_auth(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 302)

    def test_register_get(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('register'))
        self.assertContains(response, u'Registration:')
        self.assertContains(response, u'Last name')
        self.assertContains(response, u'Department')

    def test_register_post(self):
        auth_client = get_auth_client()
        year = Year.objects.create(year=u'2016')
        dept = Department.objects.create(name=u'Engineering')
        degree = Degree.objects.create(abbreviation=u'Ph.D', name=u'Doctor')
        data = {u'last_name': u'smîth', u'first_name': u't©m',
                u'address_street': u'123 Some Rd.', u'address_city': u'Ville',
                u'address_state': u'RI', u'address_zip': u'12345-5423',
                u'email': u'tsmith@brown.edu', u'phone': u'401-123-1234',
                u'year': year.id, u'department': dept.id, u'degree': degree.id}
        response = auth_client.post(reverse('register'), data)
        self.assertEqual(Person.objects.all()[0].last_name, u'smîth')
        self.assertEqual(Candidate.objects.all()[0].person.last_name, u'smîth')
