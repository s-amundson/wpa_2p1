import json
import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse

from ..models import PaymentLog, User
from ..src.square_helper import SquareHelper

logger = logging.getLogger(__name__)


class TestsPayment(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def eval_content(self, content, status, error, length):
        logging.debug(content)
        self.assertEqual(content['status'], status)
        self.assertEqual(content['error'], error)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), length)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        session = self.client.session
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [SquareHelper().line_item(f"Class on None student id: 1", 1, 5), ]
        session.save()

    def test_payment_success(self):
        # process a good payment
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'COMPLETED', [], 1)

    def test_payment_card_decline(self):
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-declined'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Card was declined, ', 0)

    def test_payment_card_bad_cvv(self):
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', 0)

    def test_payment_card_bad_expire_date(self):
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-expiration'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Invalid expiration date, ', 0)

    def test_payment_without_uuid(self):
        session = self.client.session
        del session['idempotency_key']
        session.save()
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'payment processing error', 0)
