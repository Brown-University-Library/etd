# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase


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
