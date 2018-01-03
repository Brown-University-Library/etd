from datetime import datetime
from django.core import mail
from django.test import TestCase
from tests.test_models import LAST_NAME, FIRST_NAME
from tests.test_views import CandidateCreator
from etd_app import email
from etd_app.models import Degree


class TestEmail(TestCase, CandidateCreator):

    def test_send_submit_email_to_gradschool(self):
        self._create_candidate()
        email.send_submit_email_to_gradschool(self.candidate)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'PhD Dissertation submitted')

    def test_accept_params(self):
        self._create_candidate()
        params = email._accept_params(self.candidate)
        self.assertEqual(params['subject'], 'Dissertation Submission Approved')
        self.assertTrue('Dear %s %s' % (FIRST_NAME, LAST_NAME) in params['message'])
        self.assertEqual(params['to_address'], ['tom_jones@brown.edu'])

    def test_accept_params_masters(self):
        self._create_candidate(degree_type=Degree.TYPES.masters)
        params = email._accept_params(self.candidate)
        self.assertEqual(params['subject'], 'Thesis Submission Approved')
        self.assertTrue('Dear %s %s' % (FIRST_NAME, LAST_NAME) in params['message'])
        self.assertEqual(params['to_address'], ['tom_jones@brown.edu'])

    def test_reject_params(self):
        self._create_candidate()
        gen_comments = 'Here are my general comments.'
        self.candidate.thesis.format_checklist.general_comments = gen_comments
        self.candidate.thesis.format_checklist.save()
        params = email._reject_params(self.candidate)
        self.assertEqual(params['subject'], 'Dissertation Submission Rejected')
        self.assertTrue(gen_comments in params['message'])

    def test_reject_params_masters(self):
        self._create_candidate(degree_type=Degree.TYPES.masters)
        gen_comments = 'Here are my general comments.'
        self.candidate.thesis.format_checklist.general_comments = gen_comments
        self.candidate.thesis.format_checklist.save()
        params = email._reject_params(self.candidate)
        self.assertEqual(params['subject'], 'Thesis Submission Rejected')
        self.assertTrue(gen_comments in params['message'])
        self.assertTrue('dissertation' not in params['message'])
        self.assertTrue('thesis' in params['message'])

    def test_complete_params_masters(self):
        self._create_candidate(degree_type=Degree.TYPES.masters)
        params = email._complete_params(self.candidate)
        self.assertTrue('dissertation' not in params['message'])
        self.assertTrue('masters degree' in params['message'])

    def test_paperwork_params(self):
        self._create_candidate()
        params = email._paperwork_params(self.candidate, 'dissertation_fee')
        self.assertEqual(params['subject'], 'Dissertation Fee')

    def test_now(self):
        date_display = email._format_datetime_display(datetime(2016, 4, 12, 11, 39, 55))
        self.assertEqual(date_display, '04/12/2016 at 11:39')
