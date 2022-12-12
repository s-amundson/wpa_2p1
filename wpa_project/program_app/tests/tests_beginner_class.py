import logging
import uuid
from django.db.models import Q
from datetime import date
from django.apps import apps
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch

from ..models import BeginnerClass
from ..tasks import refund_class
from event.models import Event, Registration
from payment.models import PaymentLog
from payment.tests import MockSideEffects
from student_app.models import Student

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsBeginnerClass(MockSideEffects, TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_UID = 3

    def create_payment(self, students, amount=500):
        ik = uuid.uuid4()
        for student in students:
            Registration.objects.create(
                event=Event.objects.get(pk=1),
                student=student,
                pay_status="paid",
                idempotency_key=ik,
                reg_time="2021-06-09",
                attended=False
            )
        PaymentLog.objects.create(
            category='joad',
            checkout_created_time=timezone.now(),
            description='programs_test',  # database set to 255 characters
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
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.class_dict = {'class_date': "2021-05-30T16:00:00.000Z",
                           'class_type': 'combined',
                           'beginner_limit': 2,
                           'beginner_wait_limit': 0,
                           'returnee_limit': 2,
                           'returnee_wait_limit': 0,
                           'instructor_limit': 2,
                           'state': 'scheduled',
                           'cost': 5}

    def test_user_normal_user_not_authorized(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('programs:beginner_class'), secure=True)
        self.assertEqual(response.status_code, 403)
        # Post the page user is forbidden
        response = self.client.post(reverse('programs:beginner_class'), self.class_dict, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_board_user_is_authorized(self):
        # allow user to access
        response = self.client.get(reverse('programs:beginner_class'), secure=True)
        self.assertEqual(response.context['form'].initial['beginner_limit'], 20)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/beginner_class.html')
        self.assertEqual(response.context['form'].initial['class_date'].day, date(2022, 6, 19).day)
        self.assertEqual(response.context['form'].initial['class_date'].month, date(2022, 6, 19).month)

    def test_add_class(self):
        # Add a class
        response = self.client.post(reverse('programs:beginner_class'), self.class_dict, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 3)

    def test_get_class_list(self):
        # Check the list
        response = self.client.get(reverse('programs:class_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('program_app/class_list.html')

    def test_update_class(self):
        # Update the class
        self.class_dict['state'] = 'open'
        self.class_dict['class_date'] = '2022-05-30'
        response = self.client.post(reverse('programs:beginner_class', kwargs={'beginner_class': 1}),
                                    self.class_dict, secure=True)

        self.assertTemplateUsed('student_app/index.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 2)
        bc = BeginnerClass.objects.get(pk=1)

        self.assertEqual(bc.event.event_date.year, date(2022, 5, 30).year)
        self.assertEqual(bc.event.state, 'open')

    def test_2nd_class_error(self):
        bc = BeginnerClass.objects.get(pk=1)
        # New class same day
        self.class_dict['class_date'] = '2023-06-05 09:00'
        response = self.client.post(reverse('programs:beginner_class'), self.class_dict, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 2)

    def test_2nd_class_good(self):
        bc = BeginnerClass.objects.get(pk=1)
        # New class same day
        self.class_dict['class_date'] = "2022-06-05 07:00"
        response = self.client.post(reverse('programs:beginner_class'), self.class_dict, secure=True)
        self.assertRedirects(response, reverse('programs:class_list'))
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 3)

    def test_add_class_invalid(self):
        # New class different day invalid
        response = self.client.post(reverse('programs:beginner_class'),
                        {'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 2)

    @patch('program_app.forms.unregister_form.RefundHelper.refund_payment')
    def test_refund_success_class(self, refund):
        refund.side_effect = self.refund_side_effect

        self.test_user = User.objects.get(pk=2)
        self.test_user.is_staff = False
        self.test_user.save()
        self.client.force_login(self.test_user)

        self.create_payment([Student.objects.get(pk=2), Student.objects.get(pk=3)], 1000)

        #  Change user and make another payment
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        s = Student.objects.get(pk=5)
        s.user = None
        s.save()
        self.create_payment([s], 500)

        #  Change user and then cancel the class
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.class_dict['state'] = 'canceled'
        self.class_dict['cancel_message'] = 'due to extreme bytes'
        response = self.client.post(reverse('programs:beginner_class', kwargs={'beginner_class': 1}),
                                    self.class_dict, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        refund_class(bc, 'due to extreme bytes') # this is typically called by celery
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 3)
        for c in cr:
            self.assertEqual(c.pay_status, 'refund')

        self.assertEqual(bc.event.state, 'canceled')
        pl = PaymentLog.objects.filter(Q(idempotency_key=cr[0].idempotency_key) | Q(idempotency_key=cr[2].idempotency_key))
        self.assertEqual(len(pl), 2)
        for l in pl:
            self.assertEqual(l.status, 'refund')
        # logging.warning(mail.outbox[0].body)

    def test_beginner_class_with_returnee(self):
        self.class_dict['class_type'] = 'beginner'
        response = self.client.post(reverse('programs:beginner_class'), self.class_dict, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 3)
        self.assertEqual(bc[2].returnee_limit, 0)

    def test_returnee_class_with_beginner(self):
        self.class_dict['class_type'] = 'returnee'
        response = self.client.post(reverse('programs:beginner_class'), self.class_dict, secure=True)
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 3)
        # self.assertEqual(self.client.session['message'], "returning class can't have a beginner limit greater then 0")
        self.assertEqual(bc[2].beginner_limit, 0)


class TestsBeginnerClass2(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_no_records(self):
        # allow user to access
        response = self.client.get(reverse('programs:beginner_class'), secure=True)
        self.assertEqual(response.context['form'].initial['beginner_limit'], 20)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/beginner_class.html')
