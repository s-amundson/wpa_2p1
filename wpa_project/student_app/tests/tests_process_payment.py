import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse

from ..models import ClassRegistration, PaymentLog, User
from ..src import SquareHelper

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

    def test_bypass(self):
        response = self.client.post(reverse('registration:process_payment'),
                                    {'bypass': ''}, secure=True)
        self.assertTemplateUsed('student_app/message.html')
        self.assertContains(response, 'payment successful')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)

    def test_refund_class_registration_payment(self):
        session = self.client.session
        del session['idempotency_key']
        del session['line_items']
        session.save()

        ClassRegistration(beginner_class_id=1, student_id=2, new_student=True, pay_status='paid',
                          idempotency_key='7cd7b257-d136-47f7-86a7-d9e34cba81ce', reg_time='2020-06-07').save()
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        # TODO this needs to be completed