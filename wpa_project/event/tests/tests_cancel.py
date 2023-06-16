import logging
import uuid
from unittest.mock import patch
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from program_app.tests.helper import create_beginner_class
from event.models import Event, Registration
from student_app.models import Student, User
from payment.models import PaymentLog, RefundLog
from payment.tests import MockSideEffects
logger = logging.getLogger(__name__)


class TestsCancel(MockSideEffects, TestCase):
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
        self.test_url = reverse('events:cancel')
        self.url_registration = reverse('programs:class_registration')
        self.client.force_login(self.test_user)
        self.post_dict = {
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 2,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-0-student': 2,
            'form-0-id': 11,
            'form-0-cancel': True,
            'form-1-student': 3,
            'form-1-id': 12,
            'form-1-cancel': False,
            'donate': False,
        }

    def create_register_class(self, days=4, state='open'):
        bc = create_beginner_class(
            date=timezone.now() + timezone.timedelta(days=days),
            state=state,
            class_type='beginner'
        )
        pay_status = 'paid'
        if state == 'wait':
            bc.beginner_limit = 1
            bc.beginner_wait_limit = 5
            bc.returnee_limit = 0
            bc.returnee_wait_limit = 0
            bc.save()
            pay_status = 'waiting'
        elif state == 'start':
            bc.event.state = 'open'
            pay_status = 'start'
        ik = uuid.uuid4()
        students = self.test_user.student_set.first().student_family.student_set.all()
        reg = []
        for student in students:
            r = Registration.objects.create(
                event=bc.event,
                student=student,
                pay_status=pay_status,
                idempotency_key=ik, reg_time="2021-06-09", attended=False
            )
            reg.append(r)
        return reg

    def test_get_cancel(self):
        self.create_register_class()

        response = self.client.get(self.test_url, secure=True)
        self.assertTemplateUsed('event/cancel.html')
        self.assertEqual(len(response.context['formset']), 2)

    @patch('event.views.cancel_view.cancel_pending.delay')
    def test_post_cancel(self, task_cancel_pending):
        reg = self.create_register_class()
        self.post_dict['form-0-id'] = reg[0].id
        self.post_dict['form-0-cancel'] = False
        self.post_dict['form-1-id'] = reg[1].id
        self.post_dict['form-1-cancel'] = True

        response = self.client.post(self.test_url, self.post_dict, secure=True)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'paid')
        self.assertEqual(registrations[1].pay_status, 'cancel_pending')
        task_cancel_pending.assert_called_with([reg[1].id], False)

    @patch('event.views.cancel_view.cancel_pending.delay')
    def test_post_cancel_admin(self, task_cancel_pending):
        reg = self.create_register_class()
        self.test_user = User.objects.get(pk=1)
        self.test_url = reverse('events:cancel', kwargs={'student_family': 2})
        self.client.force_login(self.test_user)
        self.post_dict['form-0-id'] = reg[0].id
        self.post_dict['form-0-cancel'] = False
        self.post_dict['form-1-id'] = reg[1].id
        self.post_dict['form-1-cancel'] = True

        response = self.client.post(self.test_url, self.post_dict, secure=True)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'paid')
        self.assertEqual(registrations[1].pay_status, 'cancel_pending')
        task_cancel_pending.assert_called_with([reg[1].id], False)
        self.assertRedirects(response, self.test_url)

    def test_post_cancel_within_24_hours(self):
        reg = self.create_register_class()
        reg[0].event.event_date = timezone.now() + timedelta(hours=12)
        reg[0].event.save()
        self.post_dict['form-0-id'] = reg[0].id
        self.post_dict['form-0-cancel'] = False
        self.post_dict['form-1-id'] = reg[1].id
        self.post_dict['form-1-cancel'] = True

        response = self.client.post(self.test_url, self.post_dict, secure=True)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'paid')
        self.assertEqual(registrations[1].pay_status, 'cancel_pending')

    def test_cancel_waiting(self):
        reg = self.create_register_class(state='wait')
        reg[0].event.event_date = timezone.now() + timedelta(hours=12)
        reg[0].event.save()
        self.post_dict['form-0-id'] = reg[0].id
        self.post_dict['form-0-cancel'] = True
        self.post_dict['form-1-id'] = reg[1].id
        self.post_dict['form-1-cancel'] = True

        response = self.client.post(self.test_url, self.post_dict, secure=True)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'canceled')
        self.assertEqual(registrations[1].pay_status, 'canceled')

    def test_cancel_incomplete_payment(self):
        reg = self.create_register_class(state='start')
        reg[0].event.event_date = timezone.now() + timedelta(hours=12)
        reg[0].event.save()
        self.post_dict['form-0-id'] = reg[0].id
        self.post_dict['form-0-cancel'] = True
        self.post_dict['form-1-id'] = reg[1].id
        self.post_dict['form-1-cancel'] = True

        response = self.client.post(self.test_url, self.post_dict, secure=True)

        registrations = Registration.objects.filter(event=reg[0].event)
        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].pay_status, 'canceled')
        self.assertEqual(registrations[1].pay_status, 'canceled')
