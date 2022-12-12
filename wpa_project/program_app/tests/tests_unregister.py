import logging
import uuid
from unittest.mock import patch
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import BeginnerClass
from event.models import Event, Registration
from student_app.models import Student, User
from payment.models import PaymentLog, RefundLog
from payment.tests import MockSideEffects
logger = logging.getLogger(__name__)


class TestsUnregisterStudent(MockSideEffects, TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_payment(self, students, amount=500):
        ik = uuid.uuid4()
        for student in students:
            reg = Registration.objects.create(
                event=Event.objects.get(pk=1),
                student=student,
                pay_status="paid",
                idempotency_key=ik, reg_time="2021-06-09", attended=False
            )
        payment = PaymentLog.objects.create(
            category='joad',
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
            total_money=amount,
            user=self.test_user
        )

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.test_url = reverse('programs:unregister')
        self.url_registration = reverse('programs:class_registration')
        self.client.force_login(self.test_user)

    @patch('program_app.forms.unregister_form.RefundHelper.refund_payment')
    @patch('program_app.forms.unregister_form.update_waiting.delay')
    def test_refund_success_entire_purchase(self, task_update_waiting, refund):

        refund.side_effect = self.refund_side_effect
        student = Student.objects.get(pk=2)
        student.user.is_staff = False
        student.user.save()

        self.create_payment([student, Student.objects.get(pk=3)], 1000)
        cr = Registration.objects.all()
        logging.debug(cr)

        # make student a returnee and the class full
        student = Student.objects.get(pk=3)
        student.safety_class = '2020-01-01'
        student.save()
        bc = BeginnerClass.objects.get(pk=1)
        bc.state = 'full'
        bc.save()
        d = {'donation': False}
        for r in cr:
            d[f'unreg_{r.id}'] = True
        response = self.client.post(self.test_url, d, secure=True)
        self.assertRedirects(response, self.url_registration)

        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].amount, 1000)
        pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')
        # refund.assert_called_with(pl[0].idempotency_key, 1000)

        cr = bc.event.registration_set.all()
        self.assertEqual(cr[0].pay_status, 'refunded')
        self.assertEqual(cr[1].pay_status, 'refunded')
        task_update_waiting.assert_called_with(1)

    @patch('program_app.forms.unregister_form.RefundHelper.refund_payment')
    @patch('program_app.forms.unregister_form.update_waiting.delay')
    def test_refund_success_partial_purchase(self, task_update_waiting, refund):
        refund.side_effect = self.refund_side_effect
        self.create_payment([Student.objects.get(pk=2), Student.objects.get(pk=3)], 1000)
        cr = Registration.objects.all()

        d = {'donation': False, f'unreg_{cr[0].id}': True}
        response = self.client.post(self.test_url, d, secure=True)
        self.assertRedirects(response, self.url_registration)

        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].amount, 500)
        pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')

        # refund the other one as well but mark both.
        d = {'donation': False}
        for r in cr:
            d[f'unreg_{r.id}'] = True
        response = self.client.post(self.test_url, d, secure=True)
        self.assertRedirects(response, self.url_registration)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 2)
        self.assertEqual(rl[1].amount, 500)
        pl = PaymentLog.objects.filter(payment_id=rl[1].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')
        task_update_waiting.assert_called_with(1)

    @patch('program_app.forms.unregister_form.RefundHelper.refund_payment')
    @patch('program_app.forms.unregister_form.update_waiting.delay')
    def test_donate_refund(self, task_update_waiting, refund):
        refund.side_effect = self.refund_side_effect
        student = Student.objects.get(pk=2)
        student.user.is_staff = False
        student.user.save()

        self.create_payment([student, Student.objects.get(pk=3)], 1000)
        cr = Registration.objects.all()
        d = {'donation': True}
        for r in cr:
            d[f'unreg_{r.id}'] = True
        response = self.client.post(self.test_url, d, secure=True)
        self.assertRedirects(response, self.url_registration)
        cr = Registration.objects.all()
        for r in cr:
            self.assertEqual(r.pay_status, 'refund donated')
        task_update_waiting.assert_called_with(1)

    def test_cancel_waiting(self):
        ik = uuid.uuid4()
        students = [Student.objects.get(pk=2), Student.objects.get(pk=3)]
        for student in students:
            reg = Registration.objects.create(
                event=Event.objects.get(pk=1),
                student=student,
                pay_status="waiting",
                idempotency_key=ik, reg_time="2021-06-09", attended=False
            )
        cr = Registration.objects.all()
        d = {'donation': True}
        for r in cr:
            d[f'unreg_{r.id}'] = True
        response = self.client.post(self.test_url, d, secure=True)
        self.assertRedirects(response, self.url_registration)
        cr = Registration.objects.all()
        for r in cr:
            self.assertEqual(r.pay_status, 'canceled')

    def test_cancel_within_24hrs(self):
        student = Student.objects.get(pk=2)
        student.user.is_staff = False
        student.user.save()

        self.create_payment([student, Student.objects.get(pk=3)], 1000)
        cr = Registration.objects.all()
        logging.debug(cr)
        bc = BeginnerClass.objects.get(pk=1)
        class_date = timezone.now() + timedelta(hours=18)
        bc.event.event_date = bc.event.event_date.replace(year=class_date.year, month=class_date.month, day=class_date.day)
        bc.event.state = 'closed'
        bc.event.save()
        logging.warning(bc.event.event_date)

        d = {'donation': False}
        for r in cr:
            d[f'unreg_{r.id}'] = True
        response = self.client.post(self.test_url, d, secure=True)
        self.assertRedirects(response, self.url_registration)

        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'closed')

        cr = bc.event.registration_set.all()
        self.assertEqual(cr[0].pay_status, 'canceled')
        self.assertEqual(cr[1].pay_status, 'canceled')


class TestsUnregisterStudent2(TestCase):
    fixtures = ['f1', 'f2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.test_url = reverse('programs:unregister')
        self.url_registration = reverse('programs:class_registration')
        self.client.force_login(self.test_user)

    def test_refund_invalid_student(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(self.test_url, {'unreg_1': True, 'unreg_2': True, 'donation': True}, secure=True)
        self.assertRedirects(response, self.url_registration)

    def test_refund_class_wrong(self):  # requires fixture f2
        bc = BeginnerClass.objects.get(pk=1)
        for state in ['closed', 'canceled', 'recorded']:
            bc.state = state
            bc.save()
            response = self.client.post(self.test_url, {'unreg_1': True, 'unreg_2': True, 'donation': False}, secure=True)
            self.assertRedirects(response, self.url_registration)

    def test_unregister_expired(self):
        # set the time of the class within 24 hours.
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_date = datetime.now() + timedelta(hours=20)
        bc.save()

        response = self.client.post(self.test_url, {'unreg_1': True, 'unreg_2': True, 'donation': False}, secure=True)
        self.assertRedirects(response, self.url_registration)
