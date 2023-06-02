import logging
import uuid
from unittest.mock import patch
from django.test import TestCase, Client
from django.core import mail

from ..tasks import close_create_class, daily_update, reminder_email, wait_list_email
from event.models import Registration, Event
from payment.tests import MockSideEffects
from student_app.models import Student
logger = logging.getLogger(__name__)


class TestsTasks(MockSideEffects, TestCase):
    fixtures = ['f1', 'beginner_schedule']

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

    def test_wait_list_email_one(self):
        # put a record in to the database
        student = Student.objects.get(pk=4)
        ik = uuid.uuid4()
        cr = Registration.objects.create(
            event=Event.objects.get(pk=1),
            student=student,
            pay_status='paid',
            idempotency_key=ik,
            user=student.user,
        )
        wait_list_email([cr.id])
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(str(mail.outbox[0].message()).count('If a spot opens up') == 2)
        self.assertTrue(str(mail.outbox[0].message()).count('Charles Wells') == 2)
        self.assertTrue(str(mail.outbox[0].message()).count('Gary Wells') == 0)

    def test_wait_list_email_multiple(self):
        # put a record in to the database
        student = Student.objects.get(pk=4)
        ik = uuid.uuid4()
        cr1 = Registration.objects.create(
            event=Event.objects.get(pk=1),
            student=student,
            pay_status='paid',
            idempotency_key=ik,
            user=student.user,
        )
        cr2 = Registration.objects.create(
            event=Event.objects.get(pk=1),
            student=Student.objects.get(pk=5),
            pay_status='paid',
            idempotency_key=ik,
            user=student.user,
        )
        wait_list_email([cr1.id, cr2.id])
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(str(mail.outbox[0].message()).count('If 2 spots open up') == 2)
        self.assertTrue(str(mail.outbox[0].message()).count('Charles Wells') == 2)
        self.assertTrue(str(mail.outbox[0].message()).count('Gary Wells') == 2)

