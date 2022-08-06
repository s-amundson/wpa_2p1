import logging
import uuid

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from student_app.models import Student
from ..models import Session, Registration
from payment.models import PaymentLog, RefundLog

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadRegistrationCancel(TestCase):
    fixtures = ['f1', 'joad1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings.SQUARE_TESTING = True

    def create_payment(self, amount=12500):
        ik = uuid.uuid4()
        reg = Registration.objects.create(session=Session.objects.get(pk=1),
                                          student=Student.objects.get(pk=8), pay_status='paid', idempotency_key=ik)
        payment = PaymentLog.objects.create(
            category='joad',
            checkout_created_time=timezone.now(),
            description='joad_test',  # database set to 255 characters
            donation=0,  # storing pennies in the database
            idempotency_key=ik,
            location_id='',
            order_id='',
            payment_id='test_payment',
            receipt='',
            source_type='',
            status='SUCCESS',
            total_money=amount,
            user=self.test_user
        )

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.student_dict = {'session': 1, 'student_8': True}
        self.test_url = reverse('joad:registration_cancel', kwargs={'session_id': 1})
        self.pay_dict = {'amount': 125, 'card': 0, 'donation': 0, 'category': 'joad', 'save_card': False,
                         'source_id': 'cnon:card-nonce-ok'}

    def test_no_user_get(self):
        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(response.status_code, 302)

    def test_no_student_family_get(self):
        student = Student.objects.get(pk=4)
        student.student_family = None
        student.save()
        self.client.force_login(student.user)
        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_user_normal_get_no_student(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(response.context['form'].student_count, 0)
        self.assertTemplateUsed(response, 'joad/registration.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(response.context['form'].student_count, 0)
        self.assertTemplateUsed(response, 'joad/registration.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_user_get_existing(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.create_payment()

        response = self.client.get(reverse('joad:registration_cancel', kwargs={'session_id': 1}), secure=True)
        self.assertEqual(response.context['form'].student_count, 1)
        self.assertTemplateUsed(response, 'joad/registration.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_post(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.create_payment()

        reg = Registration.objects.all()
        logging.debug(reg)

        response = self.client.post(self.test_url, self.student_dict, secure=True)

        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].amount, 12500)
        pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')

        reg = Registration.objects.all()
        self.assertEqual(len(reg), 1)
        self.assertEqual(reg[0].pay_status, 'refunded')

    def test_user_post_good(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        self.create_payment()

        response = self.client.post(self.test_url, self.student_dict, secure=True)
        self.assertRedirects(response, reverse('joad:index'))

        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].amount, 12500)
        pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')

        reg = Registration.objects.all()
        self.assertEqual(len(reg), 1)
        self.assertEqual(reg[0].pay_status, 'refunded')

    def test_user_post_bad(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        self.create_payment()

        self.test_user = User.objects.get(pk=5)
        self.client.force_login(self.test_user)

        response = self.client.post(self.test_url, self.student_dict, secure=True)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 0)

    def test_user_post_session_closed(self):
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        self.create_payment()

        session = Session.objects.get(pk=1)
        session.state = 'closed'
        session.save()

        response = self.client.post(self.test_url, self.student_dict, secure=True)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 0)
        self.assertContains(response, 'Select a valid choice. That choice is not one of the available choices.')
