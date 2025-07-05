import logging
import uuid
from unittest.mock import patch
from django.test import TestCase, Client, tag
from django.utils import timezone
from django.db.models import signals
from django.core import mail
from django.contrib.auth.models import Group

from program_app.tests.helper import create_beginner_class
from event.models import Registration
from event.signals import registration_update
from ..tasks import cancel_pending
from student_app.models import Student, User
from payment.models import PaymentLog
from payment.tests import MockSideEffects
logger = logging.getLogger(__name__)


@patch('event.tasks.EmailMessage.refund_email')
@patch('event.tasks.RefundHelper.refund_payment')
class TestsEventTasks(MockSideEffects, TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        signals.post_save.disconnect(sender=PaymentLog, dispatch_uid='registration_update')

    @classmethod
    def tearDownClass(cls):
        signals.post_save.connect(registration_update, sender=PaymentLog, dispatch_uid='registration_update')
        super().tearDownClass()

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.staff_group = Group.objects.get(name='staff')
        self.instructors_group = Group.objects.get(name='instructors')
        self.payments = []

    def create_register_class(self, payment=True, days=4, amount=500):

        bc = create_beginner_class(
            date=timezone.now() + timezone.timedelta(days=days),
            state='open',
            class_type='beginner'
        )
        ik = uuid.uuid4()
        students = self.test_user.student_set.first().student_family.student_set.all()
        reg = []
        for student in students:
            r = Registration.objects.create(
                event=bc.event,
                student=student,
                pay_status="cancel_pending",
                idempotency_key=ik,
                reg_time="2021-06-09",
                attended=False,
                user=self.test_user
            )
            reg.append(r)
        if payment:
            payment = PaymentLog.objects.create(
                category='class',
                checkout_created_time=timezone.now(),
                description='programs_test',  # database set to 255 characters
                donation=0,  # storing pennies in the database
                idempotency_key=ik,
                location_id='',
                order_id='',
                payment_id='test_payment',
                receipt='',
                source_type='',
                status='SUCCESS',
                total_money=amount * students.count(),
                user=self.test_user
            )
            self.payments.append(payment)
        return reg

    # @tag('temp')
    def test_cancel(self, refund, refund_email):
        refund.side_effect = self.refund_side_effect

        reg = self.create_register_class()
        cancel_pending([reg[0].id, reg[1].id], False)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'refunded')
        self.assertEqual(registrations[1].pay_status, 'refunded')
        refund.assert_called_with(self.payments[-1], 1000)
        refund_email.assert_called_with(self.test_user, False)

    # @tag('temp')
    def test_cancel_donate(self, refund, refund_email):
        refund.side_effect = self.refund_side_effect

        reg = self.create_register_class()
        cancel_pending([reg[0].id, reg[1].id], True)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'refund donated')
        self.assertEqual(registrations[1].pay_status, 'refund donated')
        self.assertFalse(refund.called)
        refund_email.assert_called_with(self.test_user, True)

    # @tag('temp')
    def test_cancel_partial(self, refund, refund_email):
        refund.side_effect = self.refund_side_effect

        reg = self.create_register_class()
        reg[1].pay_status = 'paid'
        reg[1].save()
        cancel_pending([reg[0].id], False)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'refunded')
        self.assertEqual(registrations[1].pay_status, 'paid')
        self.assertTrue(refund.called)
        refund.assert_called_with(self.payments[-1], 500)
        refund_email.assert_called_with(self.test_user, False)

    # @tag('temp')
    def test_cancel_within_24_hours(self, refund, refund_email):
        refund.side_effect = self.refund_side_effect

        reg = self.create_register_class()
        reg[0].event.event_date = timezone.now() + timezone.timedelta(hours=12)
        reg[0].event.save()
        cancel_pending([reg[0].id, reg[1].id], False)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'canceled')
        self.assertEqual(registrations[1].pay_status, 'canceled')
        self.assertFalse(refund.called)
        self.assertFalse(refund_email.called)

    def test_cancel_work(self, refund, refund_email):
        refund.side_effect = self.refund_side_effect

        reg = self.create_register_class(payment=False)
        reg[0].event.type = 'work'
        reg[0].event.save()
        cancel_pending([reg[0].id, reg[1].id], False)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'canceled')
        self.assertEqual(registrations[1].pay_status, 'canceled')
        self.assertFalse(refund.called)
        self.assertFalse(refund_email.called)

    # @tag('temp')
    def test_cancel_staff_within_24_hours(self, refund, refund_email):
        refund.side_effect = self.refund_side_effect

        user = User.objects.create(username="john", email="john@example.org")
        user.groups.add(self.staff_group)
        reg2 = self.create_register_class(payment=False)
        reg2[0].event.event_date = timezone.now() + timezone.timedelta(hours=12)
        reg2[0].event.save()
        reg2[1].student.user = user
        reg2[1].student.save()

        cancel_pending([reg2[0].id, reg2[1].id], False)

        registrations = Registration.objects.filter(event=reg2[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(Registration.objects.get(pk=reg2[0].id).pay_status, 'canceled')
        self.assertEqual(Registration.objects.get(pk=reg2[1].id).pay_status, 'canceled')
        self.assertFalse(refund.called)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Instructor Cancellation')
        self.assertFalse(refund_email.called)

    # @tag('temp')
    def test_cancel_staff_within_24_hours_no_email(self, refund, refund_email):
        refund.side_effect = self.refund_side_effect

        user = User.objects.create(username="john", email="john@example.org")
        user.groups.add(self.staff_group)
        reg2 = self.create_register_class(payment=False)
        reg2[0].event.event_date = timezone.now() + timezone.timedelta(hours=12)
        reg2[0].event.save()
        reg2[1].student.user = user
        reg2[1].student.save()

        # create some more instructors to so that we can test removing staff without sending email
        self.test_user = User.objects.get(pk=5)
        self.test_user.groups.add(self.staff_group, self.instructors_group)

        # self.test_user.save()
        sf = self.test_user.student_set.first().student_family
        ik = uuid.uuid4()
        for i in range(5):
            student = Student.objects.create(
                first_name=f'john{i}',
                last_name='doe',
                dob='1971-07-22',
                student_family=sf,
                email=f'john{i}@example.org',
                user=User.objects.create(
                    username=f'john{i}@example.org',
                    email=f'john{i}@example.org'
                )
            )
            student.user.groups.add(self.staff_group, self.instructors_group)
            r = Registration.objects.create(
                event=reg2[0].event,
                student=student,
                pay_status="paid",
                idempotency_key=ik,
                reg_time="2021-06-09",
                attended=False,
                user=self.test_user
            )

        cancel_pending([reg2[0].id, reg2[1].id], False)

        registrations = Registration.objects.filter(event=reg2[0].event)
        self.assertEqual(len(registrations), 7)
        self.assertEqual(Registration.objects.get(pk=reg2[0].id).pay_status, 'canceled')
        self.assertEqual(Registration.objects.get(pk=reg2[1].id).pay_status, 'canceled')
        self.assertFalse(refund.called)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(refund_email.called)
