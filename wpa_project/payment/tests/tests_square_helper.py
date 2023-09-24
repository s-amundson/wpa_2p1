import logging
import uuid

from django.test import TestCase, Client, tag
from django.apps import apps
from django.core import mail

from ..models import Card, Customer, PaymentLog
from ..src import CardHelper, CustomerHelper, PaymentHelper

logger = logging.getLogger(__name__)


class TestsSquareHelper(TestCase):
    fixtures = ['f1', 'square_1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        self.customer = Customer.objects.get(pk=1)

    # @tag('temp')
    def test_payment_create_good(self):
        payment = PaymentHelper(user=self.test_user)
        payment_log, created = payment.create_payment(
            amount=5,
            category='donation',
            donation=0,
            idempotency_key=str(uuid.uuid4()),
            note='test payment',
            source_id='cnon:card-nonce-ok'
        )
        self.assertEqual(payment_log.status, 'COMPLETED')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)

    # @tag('temp')
    def test_payment_create_bad(self):
        payment = PaymentHelper(user=self.test_user)
        payment_log, created = payment.create_payment(
            amount=5,
            category='donation',
            donation=0,
            idempotency_key=str(uuid.uuid4()),
            note='test payment',
            source_id='cnon:card-nonce-rejected-cvv'
        )
        self.assertIsNone(payment_log)
        self.assertIn('Payment Error: CVV', payment.errors)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertTrue(mail.outbox[0].body.find('Payment Error: CVV') >= 0)

    def test_card_good(self):
        payment = PaymentHelper(user=self.test_user)
        payment_log, created = payment.create_payment(
            amount=5,
            category='donation',
            donation=0,
            idempotency_key=str(uuid.uuid4()),
            note='test payment',
            source_id='cnon:card-nonce-ok'
        )
        card_helper = CardHelper()
        card = card_helper.create_card_from_payment(self.customer, payment_log, True)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 2)
        self.assertTrue(card.default)

        # Disable card
        card = card_helper.disable_card()
        self.assertIsNotNone(card)
        self.assertFalse(card.enabled)
        self.assertFalse(card.default)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 2)

    def test_card_retrieve_good(self):
        # Retrieve the card
        card_helper = CardHelper(Card.objects.get(pk=1))
        card = card_helper.retrieve_card()
        self.assertIsNotNone(card)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 1)

    def test_card_retrieve_bad(self):
        # change the value of the card id on file
        c = Card.objects.get(pk=1)
        c.card_id = 'ccof:uIbfJXhXETSP197M3GB'
        c.save()

        # Retrieve the card
        card_helper = CardHelper(c)
        card = card_helper.retrieve_card()
        self.assertIsNone(card)
        self.assertIn('Object not found', card_helper.errors)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 1)

    def test_customer_good(self):
        customer_helper = CustomerHelper(self.test_user)
        customer = customer_helper.create_customer()
        self.assertIsNotNone(customer)
        cl = Customer.objects.all()
        self.assertEqual(len(cl), 2)

        # Retrieve Customer
        customer2 = customer_helper.retrieve_customer()
        self.assertIsNotNone(customer2)
        cl = Customer.objects.all()
        self.assertEqual(len(cl), 2)

        # Delete Customer
        deleted_customer = customer_helper.delete_customer()
        self.assertTrue(deleted_customer)

