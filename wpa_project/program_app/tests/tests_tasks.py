import logging
from unittest.mock import patch
from django.test import TestCase, Client

from ..tasks import close_create_class, daily_update, reminder_email
from payment.tests import MockSideEffects
logger = logging.getLogger(__name__)


class TestsTasks(MockSideEffects, TestCase):
    fixtures = ['beginner_schedule']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    @patch('program_app.tasks.UpdatePrograms.close_class')
    @patch('program_app.tasks.UpdatePrograms.create_class')
    def test_close_create_class(self, close_class, create_class):
        close_create_class(1)
        close_class.assert_called()
        create_class.assert_called()

    @patch('program_app.tasks.UpdatePrograms.record_classes')
    @patch('program_app.tasks.UpdatePrograms.status_email')
    def test_daily_update(self, record_classes, status_email):
        daily_update()
        record_classes.assert_called()
        status_email.assert_called()

    @patch('program_app.tasks.UpdatePrograms.reminder_email')
    def test_reminder_email(self, up_reminder_email):
        reminder_email(1)
        up_reminder_email.assert_called()
