import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Card, Customer, PaymentErrorLog
from ..src import CardHelper, PaymentHelper
logger = logging.getLogger(__name__)
User = get_user_model()


class TestsCard(TestCase):
    fixtures = ['f1', 'square_1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.url = reverse('payment:card_remove')
        self.customer = Customer.objects.get(pk=1)

    def test_get_card_remove(self):
        response = self.client.get(self.url, secure=True)
        self.assertTemplateUsed(response, 'payment/remove_card.html')

    def test_post_card_remove(self):
        old_card = Card.objects.get(pk=1)
        old_card.default = True
        old_card.enabled = True
        old_card.save()

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
        self.assertFalse(cl[0].default)

        response = self.client.post(self.url, {'card': card.id}, secure=True)
        card = Card.objects.get(pk=card.id)
        self.assertFalse(card.enabled)
        old_card = Card.objects.get(pk=1)
        self.assertTrue(old_card.default)

    def test_post_card_remove_invalid(self):
        response = self.client.post(self.url, {'card': '1'}, secure=True)
        self.assertTemplateUsed(response, 'payment/remove_card.html')

    def test_get_manage_card(self):
        response = self.client.get(reverse('payment:card_manage'), secure=True)
        self.assertTemplateUsed(response, 'payment/cards.html')

    def test_post_manage_card_good(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('payment:card_manage'),
                                    {'source_id': 'cnon:card-nonce-ok', 'default_card': True}, secure=True)
        customers = Customer.objects.all()
        self.assertEqual(len(customers), 2)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 2)
        self.assertTrue(cl[1].default)
        self.assertRedirects(response, reverse('payment:card_manage'))

    def test_post_manage_card_good_not_default(self):
        old_card = Card.objects.get(pk=1)
        old_card.default = True
        old_card.enabled = True
        old_card.save()

        response = self.client.post(reverse('payment:card_manage'),
                                    {'source_id': 'cnon:card-nonce-ok', 'default_card': False}, secure=True)
        customers = Customer.objects.all()
        self.assertEqual(len(customers), 1)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 2)
        self.assertTrue(cl[0].default)
        self.assertFalse(cl[1].default)
        self.assertRedirects(response, reverse('payment:card_manage'))

    def test_post_manage_card_bad(self):
        response = self.client.post(reverse('payment:card_manage'), {'source_id': 'cnon:card-nonce-rejected-cvv'},
                                    secure=True)
        customers = Customer.objects.all()
        self.assertEqual(len(customers), 1)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 1)
        # self.assertRedirects(response, reverse('payment:card_manage'))
        self.assertContains(response, 'Card Create Error')
        pel = PaymentErrorLog.objects.all()
        self.assertEqual(len(pel), 1)

    def test_add_force_default(self):
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
        card = card_helper.create_card_from_payment(self.customer, payment_log, False)
        cl = Card.objects.all()
        self.assertEqual(len(cl), 2)
        self.assertTrue(card.default)
        self.assertFalse(cl[0].default)
