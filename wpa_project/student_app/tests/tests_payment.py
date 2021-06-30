import json
import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse

from ..models import BeginnerClass, ClassRegistration, PaymentLog, Student, User
from ..src import SquareHelper

logger = logging.getLogger(__name__)


class TestsPayment(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def eval_content(self, content, status, error, error_continue, length):
        logging.debug(content)
        self.assertEqual(content['status'], status)
        self.assertEqual(content['error'], error)
        self.assertEqual(content['continue'], error_continue)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), length)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        session = self.client.session
        session['payment_db'] = 'ClassRegistration'
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
        session.save()

        ClassRegistration(beginner_class=BeginnerClass.objects.get(pk=1),
                          student=Student.objects.get(pk=2), new_student=True, pay_status="start",
                          idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f", reg_time="2021-06-09", attended=False)

    def test_payment_success(self):
        # process a good payment
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'COMPLETED', [], False, 1)

    def test_payment_card_decline(self):
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-declined'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Card was declined, ', True, 0)

    def test_payment_card_bad_cvv(self):
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', True, 0)

    def test_payment_card_bad_expire_date(self):
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-expiration'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Invalid expiration date, ', True, 0)

    def test_payment_without_uuid(self):
        session = self.client.session
        del session['idempotency_key']
        session.save()
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'payment processing error', False, 0)

    def test_payment_retries(self):
        #  Register student for class so we can check square_helper.payment_error
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': 1, 'student_2': 'on', 'student_3': 'on', 'terms': 'on'},
                         secure=True)
        ik = self.client.session['idempotency_key']

        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', True, 0)
        cr = ClassRegistration.objects.get(pk=1)
        self.assertNotEqual(ik, cr.idempotency_key)

        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', True, 0)
        cr = ClassRegistration.objects.get(pk=1)
        self.assertNotEqual(ik, cr.idempotency_key)

        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-expiration'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Invalid expiration date, ', False, 0)
        cr = ClassRegistration.objects.get(pk=1)
        self.assertNotEqual(ik, cr.idempotency_key)

    def test_payment_without_line_items(self):
        session = self.client.session
        del session['line_items']
        session.save()
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'missing line items.', False, 0)

    def test_payment_invalid_post(self):
        session = self.client.session
        session.save()
        response = self.client.post(reverse('registration:payment'),
                                    {'token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'payment processing error', False, 0)
