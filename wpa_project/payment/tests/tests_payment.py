import json
import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse

from student_app.models import User
from ..models import DonationLog, PaymentLog

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
        session['payment_db'] = ['program_app', 'ClassRegistration']
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
        session.save()

    def test_payment_success(self):
        # process a good payment
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'COMPLETED', [], False, 1)

    def test_payment_card_decline(self):
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-declined'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Card was declined, ', True, 0)

    def test_payment_card_bad_cvv(self):
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', True, 0)

    def test_payment_card_bad_expire_date(self):
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-expiration'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Invalid expiration date, ', True, 0)

    def test_payment_without_uuid(self):
        session = self.client.session
        del session['idempotency_key']
        session.save()
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'payment processing error', False, 0)

    # def test_payment_retries(self):
    #
    #     ik = self.client.session['idempotency_key']
    #
    #     response = self.client.post(reverse('payment:payment'),
    #                                 {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
    #     self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', True, 0)
    #     self.assertNotEqual(ik, self.client.session['idempotency_key'])
    #     self.assertEqual(self.client.session['payment_error'], 1)
    #
    #     response = self.client.post(reverse('payment:payment'),
    #                                 {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
    #     self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', True, 0)
    #     self.assertNotEqual(ik, self.client.session['idempotency_key'])
    #     self.assertEqual(self.client.session['payment_error'], 2)
    #
    #     response = self.client.post(reverse('payment:payment'),
    #                                 {'sq_token': 'cnon:card-nonce-rejected-expiration'}, secure=True)
    #     self.eval_content(json.loads(response.content), 'ERROR', 'Invalid expiration date, ', False, 0)
    #     self.assertNotEqual(ik, self.client.session['idempotency_key'])

    def test_payment_without_line_items(self):
        session = self.client.session
        del session['line_items']
        session.save()
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'missing line items.', False, 0)

    def test_payment_invalid_post(self):
        session = self.client.session
        session.save()
        response = self.client.post(reverse('payment:payment'),
                                    {'token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'payment processing error', False, 0)

    def test_payment_bypass(self):
        # process a bypass payment
        self.client.force_login(User.objects.get(pk=1))

        # have to redo session because changed user.
        session = self.client.session
        session['payment_db'] = ['program_app', 'ClassRegistration']
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
        session.save()

        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'bypass'}, secure=True)
        self.eval_content(json.loads(response.content), 'COMPLETED', [], False, 1)

    def test_cost_zero(self):
        session = self.client.session
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': '1', 'base_price_money': {'amount': 0, 'currency': 'USD'}}]
        session.save()
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'no-payment', 'donation': 0}, secure=True)
        # self.assertTemplateUsed('student_app/message.html')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'COMPLETED')

    def test_payment(self):
        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok', 'donation': 0}, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'COMPLETED')


class TestsDonationPayment(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_with_donation(self):
        session = self.client.session
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = []
        session.save()

        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok', 'donation': 5, 'note': 'donation note'},
                                    secure=True)
        dl = DonationLog.objects.all()
        self.assertEqual(len(dl), 1)
        self.assertEqual(dl[0].note, 'donation note')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(dl[0].pk, pl[0].pk)

    def test_with_donation_zero(self):
        session = self.client.session
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = []
        session.save()

        response = self.client.post(reverse('payment:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok', 'donation': 0, 'note': 'donation note'},
                                    secure=True)
        dl = DonationLog.objects.all()
        self.assertEqual(len(dl), 0)
        # self.assertEqual(dl[0].note, 'donation note')
        # pl = PaymentLog.objects.all()
        # self.assertEqual(len(pl), 1)
        # self.assertEqual(dl[0].pk, pl[0].pk)
