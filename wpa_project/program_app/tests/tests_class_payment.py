import json
import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse

from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student, User
from payment.models import PaymentLog

logger = logging.getLogger(__name__)


class TestsClassPayment(TestCase):
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
        ClassRegistration.objects.create(
            beginner_class=BeginnerClass.objects.get(pk=1),
            student=Student.objects.get(pk=4), new_student=True, pay_status="start",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f", reg_time="2021-06-09", attended=False
        )

    def test_payment_card_bad_cvv(self):
        response = self.client.post(reverse('programs:class_payment'),
                                    {'sq_token': 'cnon:card-nonce-rejected-cvv'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'Error with CVV, ', True, 0)

    def test_payment_class_full(self):

        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': 1, 'student_2': 'on', 'student_3': 'on', 'terms': 'on'},
                         secure=True)

        # add a student to the class so that when payment is processed class will be full
        ClassRegistration.objects.create(
            beginner_class=BeginnerClass.objects.get(pk=1),
            student=Student.objects.get(pk=1), new_student=True, pay_status="paid",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f", reg_time="2021-06-09", attended=False
        )

        # process a good payment
        response = self.client.post(reverse('programs:class_payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)
        self.eval_content(json.loads(response.content), 'ERROR', 'not enough space in the class', False, 0)
