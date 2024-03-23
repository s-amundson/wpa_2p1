import logging
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from ..models import Card, PaymentLog, PaymentErrorLog
from event.models import VolunteerRecord

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
        self.pay_dict = {'amount': 5, 'card': 0, 'category': 'donation', 'default_card': False, 'donation': 0,
                         'save_card': False, 'source_id': 'cnon:card-nonce-ok'}
        self.url = reverse('payment:make_payment')
        session = self.client.session
        session['line_items'] = [{'name': 'Class on None student: test_user',
                                  'quantity': 1, 'amount_each': 5}]
        session['payment_description'] = 'Class on test_date'
        session.save()

    def test_get_payment(self):
        response = self.client.get(self.url, secure=True)
        self.assertTemplateUsed(response, 'payment/make_payment.html')

    # @tag('temp')
    def test_payment_success(self):
        session = self.client.session
        session['instructions'] = "be 30 minutes early"
        session.save()
        # process a good payment
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].description, 'Class on test_date')
        self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Payment Confirmation')
        self.assertTrue(mail.outbox[0].body.find('Class on None student: test_user') >= 0)
        self.assertTrue(mail.outbox[0].body.find('be 30 minutes early') >= 0)

    # @tag('temp')
    def test_payment_success_donation_no_email(self):
        # process a good payment
        self.client.logout()
        self.pay_dict['donation'] = 5
        response = self.client.post(self.url, self.pay_dict, secure=True)
        logger.warning(response.status_code)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].donation, 500)
        self.assertEqual(len(mail.outbox), 0)

    # @tag('temp')
    def test_payment_success_donation_with_email(self):
        # process a good payment
        self.client.logout()
        self.pay_dict['donation'] = 5
        self.pay_dict['email'] = 'EmilyNConlan@einrot.com',
        response = self.client.post(self.url, self.pay_dict, secure=True)
        logger.warning(response.status_code)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].donation, 500)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].body.find('Donation   1   5    5') >= 0)

        # self.assertRedirects(response, reverse('registration:index'))
    # @tag('temp')
    def test_payment_success_donation2(self):
        # process a good payment
        self.pay_dict['donation'] = 5
        self.pay_dict['amount'] = 10
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].donation, 500)
        self.assertTrue(mail.outbox[0].body.find('Donation   1   5    5') >= 0)

    def test_payment_success_save_card_default(self):
        old_card = Card.objects.get(pk=1)
        old_card.default = True
        old_card.enabled = True
        old_card.save()
        customer = old_card.customer
        customer.user = self.test_user
        customer.save()

        # process a good payment
        self.pay_dict['save_card'] = True
        self.pay_dict['default_card'] = True
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        card = Card.objects.all()
        self.assertEqual(len(card), 2)
        self.assertEqual(card[1].customer.user, self.test_user)
        self.assertFalse(card[0].default)
        self.assertTrue(card[1].default)
        self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))

        # make payment with card
        self.pay_dict['card'] = card[1].id
        self.pay_dict['save_card'] = False
        self.pay_dict['default_card'] = False
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 2)
        card = Card.objects.all()
        self.assertEqual(len(card), 2)
        self.assertRedirects(response, reverse('payment:view_payment', args=[pl[1].id]))

    def test_payment_success_save_card(self):
        old_card = Card.objects.get(pk=1)
        old_card.default = True
        old_card.enabled = True
        old_card.save()
        customer = old_card.customer
        customer.user = self.test_user
        customer.save()

        # process a good payment
        self.pay_dict['save_card'] = True
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        card = Card.objects.all()
        self.assertEqual(len(card), 2)
        self.assertEqual(card[1].customer.user, self.test_user)
        self.assertTrue(card[0].default)
        self.assertFalse(card[1].default)
        self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))

    # @tag('temp')
    def test_payment_card_decline(self):
        self.pay_dict['source_id'] = 'cnon:card-nonce-declined'
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertTemplateUsed(response, 'payment/make_payment.html')
        self.assertTrue('Payment Error: Card Declined' in response.context['form'].payment_errors)
        pel = PaymentErrorLog.objects.all()
        self.assertEqual(len(pel), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_payment_card_bad_cvv(self):
        self.pay_dict['source_id'] = 'cnon:card-nonce-rejected-cvv'
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertTrue('Payment Error: CVV' in response.context['form'].payment_errors)
        pel = PaymentErrorLog.objects.all()
        self.assertEqual(len(pel), 1)

    def test_payment_card_bad_expire_date(self):
        self.pay_dict['source_id'] = 'cnon:card-nonce-rejected-expiration'
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertTrue('Payment Error: Expiration Date' in response.context['form'].payment_errors)
        # self.assertContains(response.context['form'].payment_errors, 'Payment Error: Expiration Date')

    def test_payment_card_sca_required(self):
        self.pay_dict['source_id'] = 'ccof:customer-card-id-requires-verification'
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        error = 'Payment Error: Strong Authentication not supported at this time, please use a different card.'
        self.assertTrue(error in response.context['form'].payment_errors)

    def test_payment_without_line_items(self):
        session = self.client.session
        del session['line_items']
        session.save()
        response = self.client.post(reverse('payment:make_payment'), self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))

    def test_payment_invalid_post(self):
        # session = self.client.session
        # session.save()
        self.pay_dict.pop('amount')
        response = self.client.post(reverse('payment:make_payment'), self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertTemplateUsed(response, 'payment/make_payment.html')

    def test_payment_invalid_amount(self):
        # session = self.client.session
        # session.save()
        self.pay_dict['amount'] = 0
        response = self.client.post(reverse('payment:make_payment'), self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertTemplateUsed(response, 'payment/make_payment.html')

    def test_payment_idempotency_key(self):
        # Use an old idempotency_key and see that it gets changed with error.
        ik = 'caf90994-d30e-4a43-8fb8-bc3e28922993'
        session = self.client.session
        session['idempotency_key'] = ik
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': 1, 'amount_each': 5}]
        session.save()

        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)
        self.assertNotEqual(self.client.session['idempotency_key'], ik)
        self.assertTemplateUsed(response, 'payment/make_payment.html')

    def test_payment_amount_zero(self):
        session = self.client.session
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': 1, 'amount_each': 0}]
        session.save()

        self.pay_dict['amount'] = 0
        self.pay_dict['source_id'] = 'no-payment'
        response = self.client.post(reverse('payment:make_payment'), self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        # self.assertTemplateUsed(response, 'payment/view_payment.html')
        self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))

    # @tag('temp')
    def test_payment_success_volunteer_points(self):
        student = self.test_user.student_set.last()
        vr = VolunteerRecord.objects.create(
            student=student,
            volunteer_points=6.5
        )
        self.pay_dict['amount'] = 5
        self.pay_dict['volunteer_points'] = 5
        self.pay_dict['source_id'] = ''

        # process a good payment
        response = self.client.post(self.url, self.pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].description, 'Class on test_date')
        self.assertEqual(pl[0].volunteer_points, 5)
        self.assertRedirects(response, reverse('payment:view_payment', args=[pl[0].id]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Payment Confirmation')
        self.assertTrue(mail.outbox[0].body.find('Class on None student: test_user') > 0)
        self.assertTrue(mail.outbox[0].body.find('Total   5') > 0)
        self.assertEqual(VolunteerRecord.objects.get_family_points(student.student_family), 1.5)
