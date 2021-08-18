import logging
import time
from django.db.models import Q
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse

from ..models import BeginnerClass, ClassRegistration, User
from payment.models import PaymentLog

logger = logging.getLogger(__name__)


class TestsBeginnerClass(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_UID = 3

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        logging.debug('here')

    def test_user_normal_user_not_authorized(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('registration:beginner_class'), secure=True)
        self.assertEqual(response.status_code, 403)
        # Post the page user is forbidden
        response = self.client.post(reverse('registration:beginner_class'),
                                    {'class_date': '2021-05-30', 'beginner_limit': 2, 'returnee_limit': 2,
                                     'state': 'scheduled', 'cost': 5}, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_staff_user_is_authorized(self):
        # allow user to access
        response = self.client.get(reverse('registration:beginner_class'), secure=True)
        self.assertEqual(response.context['form'].initial['beginner_limit'], 20)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/beginner_class.html')
        self.assertEqual(response.context['form'].initial['class_date'].day, date(2022, 6, 19).day)
        self.assertEqual(response.context['form'].initial['class_date'].month, date(2022, 6, 19).month)

    def test_add_class(self):
        # Add a class
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2023-05-30', 'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, reverse('registration:index'), status_code=301,
        #     target_status_code=200, fetch_redirect_response=True)
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 3)


    def test_get_class_list(self):
        # # allow user to access
        # self.test_user.is_staff = True
        # self.test_user.save()

        # Check the list
        response = self.client.get(reverse('registration:class_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')



    def test_update_class(self):

        # Update the class
        response = self.client.post(reverse('registration:beginner_class', kwargs={'beginner_class': 1}),
                        {'class_date': '2022-05-30', 'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'open', 'cost': 5}, secure=True)

        self.assertTemplateUsed('student_app/index.html')
        bc = BeginnerClass.objects.all()
        logging.debug(bc[0].state)
        self.assertEquals(len(bc), 2)
        bc = BeginnerClass.objects.get(pk=1)

        self.assertEqual(bc.class_date.year, date(2022, 5, 30).year)
        self.assertEqual(bc.state, 'open')

    def test_2nd_class(self):
        # New class same day
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2022-06-05', 'beginner_limit': 5, 'returnee_limit': 5,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 2)

    def test_add_class_invalid(self):
        # New class different day invalid
        response = self.client.post(reverse('registration:beginner_class'),
                        {'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 2)

    def test_refund_success_class(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '1', 'student_2': 'on', 'student_3': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        bc.beginner_limit = 4  # make space for next students
        bc.save()
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)

        # process a good payment
        response = self.client.post(reverse('registration:class_payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)

        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        logging.debug(cr[0].pay_status)

        #  Change user and make another payment
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': 1, 'student_4': 'on', 'student_5': 'on', 'terms': 'on'},
                         secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 4)

        # process a good payment
        response = self.client.post(reverse('registration:class_payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)

        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 4)
        logging.debug(cr[0].pay_status)

        # give square some time to process the payment got bad requests without it.
        time.sleep(5)

        #  Change user and then cancel the class another payment
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:beginner_class', kwargs={'beginner_class': 1}),
                                    {'class_date': "2022-06-05", 'beginner_limit': 4, 'returnee_limit': 2,
                                     'state': 'canceled', 'cost': 5}, secure=True)
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 4)
        for c in cr:
            self.assertEqual(c.pay_status, 'refund')
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'canceled')
        pl = PaymentLog.objects.filter(Q(idempotency_key=cr[0].idempotency_key) | Q(idempotency_key=cr[2].idempotency_key))
        self.assertEqual(len(pl), 2)
        for l in pl:
            self.assertEqual(l.status, 'refund')


class TestsBeginnerClass2(TestCase):
    fixtures = ['f3']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_no_records(self):
        # allow user to access
        response = self.client.get(reverse('registration:beginner_class'), secure=True)
        self.assertEqual(response.context['form'].initial['beginner_limit'], 20)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/beginner_class.html')
