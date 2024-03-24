import logging
import uuid
from unittest.mock import patch, call
from django.test import TestCase, Client, tag
from django.core import mail

from ..models import BeginnerClass
from ..tasks import charge_group, close_create_class, daily_update, reminder_email, wait_list_email, refund_class
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

    @patch('program_app.tasks.RefundHelper.refund_with_idempotency_key')
    def test_refund_class(self, refund_ik):

        # put a record in to the database
        student = Student.objects.get(pk=4)
        event = Event.objects.get(pk=1)
        ik = uuid.uuid4()
        cr1 = Registration.objects.create(
            event=event,
            student=student,
            pay_status='paid',
            idempotency_key=ik,
            user=student.user,
        )
        cr2 = Registration.objects.create(
            event=event,
            student=Student.objects.get(pk=5),
            pay_status='paid',
            idempotency_key=ik,
            user=student.user,
        )

        ik2 = uuid.uuid4()
        cr3 = Registration.objects.create(
            event=event,
            student=Student.objects.get(pk=3),
            pay_status='paid',
            idempotency_key=ik2,
            user=Student.objects.get(pk=2).user,
        )

        refund_class(BeginnerClass.objects.get(pk=1), 'due to extreme bytes')
        self.assertEqual(len(mail.outbox), 3)
        # refund_ik.assert_called_with(ik, 2 * event.cost_standard * 100)
        refund_ik.assert_called_with(ik2, 1 * event.cost_standard * 100)
        # refund_ik.assert_has_calls([
        #     call(ik, 2 * event.cost_standard * 100),
        #     call(ik2, 1 * event.cost_standard * 100)])
        self.assertEqual(refund_ik.call_count, 2)

    # @tag('temp')
    @patch('program_app.tasks.ClassRegistrationHelper.charge_group')
    def test_charge_group(self, chrg_group):
        # chrg_group.return_value = {'72eaee80-9f87-440a-9c60-a24f3feff4b3': 'SUCCESS'}
        charge_group([1])
        chrg_group.assert_called()
