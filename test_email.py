from django.test import TestCase
from .test_models import LAST_NAME, FIRST_NAME
from .test_views import CandidateCreator
from . import email


class TestEmail(TestCase, CandidateCreator):

    def test_accept_params(self):
        self._create_candidate()
        params = email._accept_params(self.candidate)
        self.assertEqual(params['subject'], u'Dissertation Submission Approved')
        self.assertTrue('Dear %s %s' % (FIRST_NAME, LAST_NAME) in params['message'])
        self.assertEqual(params['to_address'], ['tom_jones@brown.edu'])

    def test_reject_params(self):
        self._create_candidate()
        gen_comments = u'Here are my general comments.'
        self.candidate.thesis.format_checklist.general_comments = gen_comments
        self.candidate.thesis.format_checklist.save()
        params = email._reject_params(self.candidate)
        self.assertEqual(params['subject'], u'Dissertation Submission Rejected')
        self.assertTrue(gen_comments in params['message'])

    def test_paperwork_params(self):
        self._create_candidate()
        params = email._paperwork_params(self.candidate, 'dissertation_fee')
        self.assertEqual(params['subject'], 'Dissertation Fee')
