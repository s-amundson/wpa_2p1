import json
import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from ..models import Card, PaymentLog

logger = logging.getLogger(__name__)
User = get_user_model()


class TestsPayment(TestCase):
    fixtures = ['f1', 'square_1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        self.pay_dict = {'amount': 5, 'card': 0, 'donation': 0, 'save_card': False, 'source_id': 'cnon:card-nonce-ok'}
        # self.pay_dict['items'] = json.dumps({
        #     'name': 'widget',
        #     'quantity': str(1),
        #     'amount_each': 5,
        #      })
        self.url = reverse('payment:make_payment')
        session = self.client.session
        # # session['payment_db'] = ['program_app', 'ClassRegistration']
        # session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': 1, 'amount_each': 5}]
        session.save()

    # def test_get_payment(self):
    #     response = self.client.get(self.url, secure=True)
    #     logging.debug(response.content)


    # def test_payment_success(self):
    #     # process a good payment
    #
    #     response = self.client.post(self.url, self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 1)
    #     self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))

    # def test_payment_success_donation(self):
    #     # process a good payment
    #     self.client.logout()
    #     self.pay_dict['donation'] = 5
    #     response = self.client.post(self.url, self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 1)
    #     self.assertEqual(pl[0].donation, 5)
    #     self.assertRedirects(response, reverse('registration:index'))
    #
    # def test_payment_success_save_card(self):
    #     # process a good payment
    #     self.pay_dict['save_card'] = True
    #     response = self.client.post(self.url, self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 1)
    #     card = Card.objects.all()
    #     self.assertEqual(len(card), 2)
    #     self.assertEqual(card[1].customer.user, self.test_user)
    #     self.assertRedirects(response, reverse('square:view_payment', args=[pl[0].id]))
    #
    # def test_payment_card_decline(self):
    #     self.pay_dict['source_id'] = 'cnon:card-nonce-declined'
    #     response = self.client.post(self.url, self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 0)
    #     self.assertTemplateUsed(response, 'payment/make_payment.html')
    #     self.assertTrue('Payment Error: Card Declined' in response.context['form'].payment_errors)
    #
    # def test_payment_card_bad_cvv(self):
    #     self.pay_dict['source_id'] = 'cnon:card-nonce-rejected-cvv'
    #     response = self.client.post(self.url, self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 0)
    #     self.assertTrue('Payment Error: CVV' in response.context['form'].payment_errors)
    #
    # def test_payment_card_bad_expire_date(self):
    #     self.pay_dict['source_id'] = 'cnon:card-nonce-rejected-expiration'
    #     response = self.client.post(self.url, self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 0)
    #     self.assertTrue('Payment Error: Expiration Date' in response.context['form'].payment_errors)
    #     # self.assertContains(response.context['form'].payment_errors, 'Payment Error: Expiration Date')

    # def test_payment_card_sca_required(self):
    #     self.pay_dict['source_id'] = 'ccof:customer-card-id-requires-verification'
    #     response = self.client.post(self.url, self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 0)
    #     error = 'Payment Error: Strong Autentication not supported at this time, please use a different card.'
    #     self.assertTrue(error in response.context['form'].payment_errors)
    #
    # def test_payment_without_line_items(self):
    #     session = self.client.session
    #     del session['line_items']
    #     session.save()
    #     response = self.client.post(reverse('payment:make_payment'), self.pay_dict, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))

    def test_payment_invalid_post(self):
        # session = self.client.session
        # session.save()
        self.pay_dict.pop('amount')
        response = self.client.post(reverse('payment:make_payment'), self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertTemplateUsed(response, 'payment/make_payment.html')
    #
    # def test_payment_bypass(self):
    #     # process a bypass payment
    #     self.client.force_login(User.objects.get(pk=1))
    #
    #     # have to redo session because changed user.
    #     session = self.client.session
    #     session['payment_db'] = ['program_app', 'ClassRegistration']
    #     session['idempotency_key'] = str(uuid.uuid4())
    #     session['line_items'] = [{'name': 'Class on None student id: 1',
    #                               'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
    #     session.save()
    #
    #     response = self.client.post(reverse('payment:payment'),
    #                                 {'sq_token': 'bypass'}, secure=True)
    #     self.eval_content(json.loads(response.content), 'COMPLETED', [], False, 1)
    #
    # def test_cost_zero(self):
    #     session = self.client.session
    #     session['idempotency_key'] = str(uuid.uuid4())
    #     session['line_items'] = [{'name': 'Class on None student id: 1',
    #                               'quantity': '1', 'base_price_money': {'amount': 0, 'currency': 'USD'}}]
    #     session.save()
    #     response = self.client.post(reverse('payment:payment'),
    #                                 {'sq_token': 'no-payment', 'donation': 0}, secure=True)
    #     # self.assertTemplateUsed('student_app/message.html')
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 1)
    #     self.assertEqual(pl[0].status, 'COMPLETED')
    #
    # def test_payment(self):
    #     response = self.client.post(reverse('payment:payment'),
    #                                 {'sq_token': 'cnon:card-nonce-ok', 'donation': 0}, secure=True)
    #     pl = PaymentLog.objects.all()
    #     self.assertEqual(len(pl), 1)
    #     self.assertEqual(pl[0].status, 'COMPLETED')


# class TestsDonationPayment(TestCase):
#     fixtures = ['f1']
#
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()
#         self.test_user = User.objects.get(pk=2)
#         self.client.force_login(self.test_user)
#
#     def test_with_donation(self):
#         session = self.client.session
#         session['idempotency_key'] = str(uuid.uuid4())
#         session['line_items'] = []
#         session.save()
#
#         response = self.client.post(reverse('payment:payment'),
#                                     {'sq_token': 'cnon:card-nonce-ok', 'donation': 5, 'note': 'donation note'},
#                                     secure=True)
#         dl = DonationLog.objects.all()
#         self.assertEqual(len(dl), 1)
#         self.assertEqual(dl[0].note, 'donation note')
#         pl = PaymentLog.objects.all()
#         self.assertEqual(len(pl), 1)
#         self.assertEqual(dl[0].pk, pl[0].pk)
#
#     def test_with_donation_zero(self):
#         session = self.client.session
#         session['idempotency_key'] = str(uuid.uuid4())
#         session['line_items'] = []
#         session.save()
#
#         response = self.client.post(reverse('payment:payment'),
#                                     {'sq_token': 'cnon:card-nonce-ok', 'donation': 0, 'note': 'donation note'},
#                                     secure=True)
#         dl = DonationLog.objects.all()
#         self.assertEqual(len(dl), 0)
#         # self.assertEqual(dl[0].note, 'donation note')
#         # pl = PaymentLog.objects.all()
#         # self.assertEqual(len(pl), 1)
#         # self.assertEqual(dl[0].pk, pl[0].pk)
