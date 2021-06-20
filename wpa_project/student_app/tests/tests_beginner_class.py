import logging
import time
from django.db.models import Q
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse

from ..models import BeginnerClass, ClassRegistration, PaymentLog, User

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

    # def test_add_class(self):
    #     # Add a class
    #     response = self.client.post(reverse('registration:beginner_class'),
    #                     {'class_date': '2023-05-30', 'beginner_limit': 2, 'returnee_limit': 2,
    #                      'state': 'scheduled', 'cost': 5}, secure=True)
    #     # self.assertEqual(response.status_code, 200)
    #     # self.assertRedirects(response, reverse('registration:index'), status_code=301,
    #     #     target_status_code=200, fetch_redirect_response=True)
    #     bc = BeginnerClass.objects.all()
    #     self.assertEquals(len(bc), 3)

    def test_beginner_class(self):
        # allow user to access
        self.test_user.is_staff = True
        self.test_user.save()

        # Add a class
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2021-05-30', 'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, reverse('registration:index'), status_code=301,
        #     target_status_code=200, fetch_redirect_response=True)
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 3)

        # Check the list
        response = self.client.get(reverse('registration:class_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')

        # Update the class
        response = self.client.post(reverse('registration:beginner_class', kwargs={'beginner_class': 3}),
                        {'class_date': '2022-05-30', 'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'open', 'cost': 5}, secure=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, reverse('registration:index'))
        self.assertTemplateUsed('student_app/index.html')
        bc = BeginnerClass.objects.all()
        logging.debug(bc)
        self.assertEquals(len(bc), 3)

        # New class same day
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2022-05-30', 'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 3)

        # check get with class in database.
        response = self.client.get(reverse('registration:beginner_class'), secure=True)
        self.assertEqual(response.context['form'].initial['class_date'], date(2022, 6, 19))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/beginner_class.html')

        # New class different day
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2022-06-06', 'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        # self.assertRedirects(response, reverse('registration:index'))
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 4)

        # New class different day invalid
        response = self.client.post(reverse('registration:beginner_class'),
                        {'beginner_limit': 2, 'returnee_limit': 2,
                         'state': 'scheduled', 'cost': 5}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 4)

    def test_refund_success_class(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_2': 'on', 'student_3': 'on', 'terms': 'on'}, secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        bc.beginner_limit = 4  # make space for next students
        bc.save()
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)

        # process a good payment
        response = self.client.post(reverse('registration:payment'),
                                    {'sq_token': 'cnon:card-nonce-ok'}, secure=True)

        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 2)
        logging.debug(cr[0].pay_status)

        #  Change user and make another payment
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.client.post(reverse('registration:class_registration'),
                         {'beginner_class': '2022-06-05', 'student_4': 'on', 'student_5': 'on', 'terms': 'on'},
                         secure=True)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')
        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 4)

        # process a good payment
        response = self.client.post(reverse('registration:payment'),
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
                                    {'class_date': '2022-06-05', 'beginner_limit': 4, 'returnee_limit': 2,
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
