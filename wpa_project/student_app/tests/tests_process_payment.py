import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse

from ..models import PaymentLog, User
from ..src.square_helper import line_item, dummy_response

logger = logging.getLogger(__name__)


class TestsProcessPayment(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        session = self.client.session
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [line_item(f"Class on None student id: 1", 1, 5), ]
        session.save()

    def test_get_payment_page(self):
        # Get the payment page
        response = self.client.get(reverse('registration:process_payment'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/square_pay.html')

    def test_payment_success(self):
        # process a good payment
        response = self.client.post(reverse('registration:process_payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.assertTemplateUsed('student_app/message.html')
        self.assertContains(response, 'payment successful')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)

    def test_payment_card_decline(self):
        response = self.client.post(reverse('registration:process_payment'),
                                    {'sq_token': 'cnon:card-nonce-declined'}, secure=True)
        self.assertTemplateUsed('student_app/process_payment.html')
        # self.assertContains(response, 'Card was declined,', status_code=302)
        self.assertEqual(self.client.session.get('message', ''), 'Card was declined, ')

        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)

    def test_payment_card_bad_cvv(self):
        response = self.client.post(reverse('registration:process_payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
        self.assertTemplateUsed('student_app/process_payment.html')
        # self.assertContains(response, 'Card was declined,', status_code=302)
        self.assertEqual(self.client.session.get('message', ''), 'Error with CVV, ')

        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)

    def test_payment_card_bad_expire_date(self):
        response = self.client.post(reverse('registration:process_payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-expiration'}, secure=True)
        self.assertTemplateUsed('student_app/process_payment.html')
        # self.assertContains(response, 'Card was declined,', status_code=302)
        self.assertEqual(self.client.session.get('message', ''), 'Invalid expiration date, ')

        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)

    def test_payment_without_uuid(self):
        session = self.client.session
        del session['idempotency_key']
        session.save()
        response = self.client.post(reverse('registration:process_payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.assertTemplateUsed('student_app/message.html')
        self.assertContains(response, 'payment processing error')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 0)

    def test_bypass(self):
        response = self.client.post(reverse('registration:process_payment'),
                                    {'bypass': ''}, secure=True)
        self.assertTemplateUsed('student_app/message.html')
        self.assertContains(response, 'payment successful')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
