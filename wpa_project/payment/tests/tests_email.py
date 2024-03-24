import logging

from django.apps import apps
from django.core import mail
from django.test import TestCase, Client

from ..src import EmailMessage
from event.models import Event
User = apps.get_model('student_app', 'User')
logger = logging.getLogger(__name__)


class TestsEmail(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.email_dict = {'total': 5, 'receipt': 'https://example.com',
                           'line_items': [{'name': 'Class on None student: test_user',
                                           'quantity': '1', 'amount_each': 5}]}

    def test_payment_email(self):
        EmailMessage().payment_email_user(self.test_user, self.email_dict)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Payment Confirmation')
        self.assertTrue(mail.outbox[0].body.find('Thank you for your purchase with Woodley Park Archers.') > 0)

    def test_refund_email(self):
        EmailMessage().refund_email(self.test_user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Refund Confirmation')
        s = 'Your refund with Woodley Park Archers has successfully been sent to square for processing. '
            # 'Please allow 5 to 10 business days for the refund to process.'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)
        self.assertTrue(mail.outbox[0].body.find('Thank you for your purchase with Woodley Park Archers.') < 0)

    def test_event_canceled_email(self):
        EmailMessage().event_canceled_email(self.test_user, Event.objects.get(pk=1))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Cancellation')
        s = 'Your refund with Woodley Park Archers has successfully been sent to square for processing. '
            # 'Please allow 5 to 10 business days for the refund to process.'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)
        self.assertTrue(mail.outbox[0].body.find('Thank you for your purchase with Woodley Park Archers.') < 0)
