import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student, User
from payment.models import PaymentLog, RefundLog
logger = logging.getLogger(__name__)


class TestsUnregisterStudent(TestCase):
    fixtures = ['f1', 'f3']
    # fixtures = ['f1', 'f2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_refund_success_entire_purchase(self):
        student = Student.objects.get(pk=2)
        student.user.is_staff = False
        student.user.save()

        self.client.post(reverse('programs:class_registration'),
                     {'beginner_class': '1', 'student_2': 'on', 'student_3': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)

        # process a good payment
        pay_dict = {'amount': 10, 'card': 0, 'donation': 0, 'category': 'intro', 'save_card': False,
                    'source_id': 'cnon:card-nonce-ok'}
        response = self.client.post(reverse('payment:make_payment'), pay_dict, secure=True)

        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        logging.debug(cr[0].pay_status)

        # give square some time to process the payment got bad requests without it.
        time.sleep(5)

        # make student a returnee and the class full
        student = Student.objects.get(pk=3)
        student.safety_class = '2020-01-01'
        student.save()
        bc = BeginnerClass.objects.get(pk=1)
        bc.state = 'full'
        bc.save()

        response = self.client.post(reverse('programs:unregister_class'),
                                    {'class_list': ['1', '2']}, secure=True)
        logging.debug(response.data)
        self.assertEqual(response.data['status'], 'SUCCESS')
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].amount, 1000)
        pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')

        cr = bc.classregistration_set.all()
        logging.debug(len(cr))
        self.assertEqual(cr[0].pay_status, 'refunded')
        self.assertEqual(cr[1].pay_status, 'refunded')

    def test_refund_success_partial_purchase(self):
        self.client.post(reverse('programs:class_registration'),
                         {'beginner_class': '1', 'student_2': 'on', 'student_3': 'on', 'terms': 'on'}, secure=True)

        # process a good payment
        pay_dict = {'amount': 10, 'card': 0, 'category': 'intro', 'donation': 0, 'save_card': False,
                    'source_id': 'cnon:card-nonce-ok'}
        response = self.client.post(reverse('payment:make_payment'),
                                    pay_dict, secure=True)
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        logging.debug(cr[0].pay_status)
        time.sleep(5)

        response = self.client.post(reverse('programs:unregister_class'),
                                    {'class_list': [cr[1].id]}, secure=True)
        logging.debug(response.data)
        self.assertEqual(response.data['status'], 'SUCCESS')
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].amount, 500)
        pl = PaymentLog.objects.filter(payment_id=rl[0].payment_id)
        self.assertEqual(len(pl), 1)
        self.assertEqual(pl[0].status, 'refund')

    def test_donate_refund(self):
        # put a record in to the database
        cr = ClassRegistration(beginner_class=BeginnerClass.objects.get(pk=1),
                               student=Student.objects.get(pk=2),
                               new_student=True,
                               pay_status='paid',
                               idempotency_key=str(uuid.uuid4()))
        cr.save()

        response = self.client.post(reverse('programs:unregister_class'),
                                    {'class_list': [cr.id], 'donation': True}, secure=True)
        cr = ClassRegistration.objects.get(pk=cr.id)
        self.assertEqual(cr.pay_status, 'refund donated')


class TestsUnregisterStudent2(TestCase):
    fixtures = ['f1', 'f2', 'f3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_refund_invalid_student(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('programs:unregister_class'),
                                    {'class_list': ['1', '2']}, secure=True)
        logging.debug(response.data)
        self.assertEqual(response.data['status'], 'ERROR')

    def test_refund_class_wrong(self):  # requires fixture f2
        bc = BeginnerClass.objects.get(pk=1)
        for state in ['closed', 'canceled', 'recorded']:
            bc.state = state
            bc.save()
            response = self.client.post(reverse('programs:unregister_class'),
                                        {'class_list': ['1', '2']}, secure=True)
            logging.debug(response.data)
            self.assertEqual(response.data['status'], 'ERROR')

    def test_unregister_expired(self):
        # set the time of the class within 24 hours.
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_date = datetime.now() + timedelta(hours=20)
        bc.save()

        response = self.client.post(reverse('programs:unregister_class'),
                                    {'class_list': ['1', '2']}, secure=True)
        logging.debug(response.data)
        self.assertEqual(response.data['status'], 'ERROR')
        self.assertEqual(response.data['error'], 'Time to unregister has passed.')
