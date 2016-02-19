# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import SimpleTestCase, TestCase
from .test_client import ETDTestClient
from .models import Person, Candidate, Year, Department, Degree


LAST_NAME = u'Jonës'
FIRST_NAME = u'T©m'


def get_auth_client():
    user = User.objects.create_user('tjones@brown.edu', 'pw')
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
        self.assertRedirects(response, '%s?next=http%%3A//testserver/register/' % settings.LOGIN_URL, fetch_redirect_response=False)

    def test_register_get(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('register'))
        self.assertContains(response, u'Registration:')
        self.assertContains(response, u'Last Name')
        self.assertContains(response, u'Department')
        self.assertNotContains(response, u'Netid')

    def test_register_post(self):
        auth_client = get_auth_client()
        year = Year.objects.create(year=u'2016')
        dept = Department.objects.create(name=u'Engineering')
        degree = Degree.objects.create(abbreviation=u'Ph.D', name=u'Doctor')
        #pass in an incorrect netid here, to make sure it's read from the username instead of
        #   the passed in value - we don't want someone to be able to register for a different user.
        data = {u'netid': u'wrongid@brown.edu', u'last_name': LAST_NAME, u'first_name': FIRST_NAME,
                u'address_street': u'123 Some Rd.', u'address_city': u'Ville',
                u'address_state': u'RI', u'address_zip': u'12345-5423',
                u'email': u'tomjones@brown.edu', u'phone': u'401-123-1234',
                u'year': year.id, u'department': dept.id, u'degree': degree.id}
        response = auth_client.post(reverse('register'), data, follow=True)
        self.assertEqual(Person.objects.all()[0].netid, u'tjones@brown.edu')
        self.assertEqual(Person.objects.all()[0].last_name, LAST_NAME)
        self.assertEqual(Candidate.objects.all()[0].person.last_name, LAST_NAME)
        self.assertRedirects(response, reverse('candidate_home'))


class TestCandidateHome(TestCase):

    def test_candidate_home_auth(self):
        response = self.client.get(reverse('candidate_home'))
        self.assertRedirects(response, '%s?next=http%%3A//testserver/candidate/' % settings.LOGIN_URL, fetch_redirect_response=False)

    def _create_candidate(self):
        year = Year.objects.create(year=u'2016')
        dept = Department.objects.create(name=u'Engineering')
        degree = Degree.objects.create(abbreviation=u'Ph.D', name=u'Doctor')
        p = Person.objects.create(netid=u'tjones@brown.edu', last_name=LAST_NAME, first_name=FIRST_NAME)
        Candidate.objects.create(person=p, year=year, department=dept, degree=degree)

    def test_candidate_get(self):
        self._create_candidate()
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertContains(response, u'%s %s' % (FIRST_NAME, LAST_NAME))

    def test_candidate_get_not_registered(self):
        auth_client = get_auth_client()
        response = auth_client.get(reverse('candidate_home'))
        self.assertRedirects(response, reverse('register'))
