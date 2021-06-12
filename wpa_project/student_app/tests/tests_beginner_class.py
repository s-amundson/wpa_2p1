import logging
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse

from ..models import BeginnerClass, User

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
