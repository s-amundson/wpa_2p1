import json
import logging
import os

import allauth
from datetime import date
from django.conf import settings
from django.template.loader import render_to_string
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from ..models import BeginnerClass

logger = logging.getLogger(__name__)

class TestsBeginnerClass(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User(email='ChristyCSnow@gustr.com', password='password', first_name='Christy',
                              last_name='Snow', is_active=True)
        self.test_user.save()
        logging.debug('here')

    # def test_login_required(self):
    #     def get_page(page, target):
    #         response = self.client.get(reverse(page))
    #         self.assertRedirects(response, f'/accounts/login/?next=/{target}')
    #
    #     get_page('registration:beginner_class', 'beginner_class')
    #     get_page('registration:class_list', 'class_list')

    def test_beginner_class(self):
        # Get the page
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:beginner_class'))
        self.assertEqual(response.context['form'].initial['beginner_limit'], 20)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/beginner_class.html')

        # Add a class
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2021-05-30', 'beginner_limit': 2, 'returnee_limit': 2, 'state': 'scheduled'})
        # self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('registration:index'))
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 1)

        # Check the list
        response = self.client.get(reverse('registration:class_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')

        # Update the class
        response = self.client.post(reverse('registration:beginner_class', kwargs={'beginner_class': 1}),
                        {'class_date': '2022-05-30', 'beginner_limit': 2, 'returnee_limit': 2, 'state': 'open'})
        # self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('registration:index'))
        bc = BeginnerClass.objects.all()
        logging.debug(bc)
        self.assertEquals(len(bc), 1)

        # New class same day
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2022-05-30', 'beginner_limit': 2, 'returnee_limit': 2, 'state': 'scheduled'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 1)

        # check get with class in database.
        response = self.client.get(reverse('registration:beginner_class'))
        self.assertEqual(response.context['form'].initial['class_date'], date(2022, 6, 6))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/beginner_class.html')

        # New class different day
        response = self.client.post(reverse('registration:beginner_class'),
                        {'class_date': '2022-06-06', 'beginner_limit': 2, 'returnee_limit': 2, 'state': 'scheduled'})
        self.assertRedirects(response, reverse('registration:index'))
        self.assertTemplateUsed('student_app/class_list.html')
        bc = BeginnerClass.objects.all()
        self.assertEquals(len(bc), 2)

        # Add a student family to do the next test.
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        self.client.post(reverse('registration:student_register'), d)
        d = {'first_name': 'Christy', 'last_name': 'Smith', 'dob': '2020-02-02'}
        self.client.post(reverse('registration:add_student'), d)
        response = self.client.get(reverse('registration:class_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/form_as_p.html')

        self.client.post(reverse('registration:class_registration'), {'beginner_class': '2022-05-30', 'student_1': 'on'})
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc[0].enrolled_beginners, 1)
        logging.debug(bc[0])

#     class_date = models.DateField()
#     enrolled_beginners = models.IntegerField(default=0)
#     beginner_limit = models.IntegerField()
#     enrolled_returnee = models.IntegerField(default=0)
#     returnee_limit = models.IntegerField()
#     states = [('scheduled', 'scheduled'), ('open', 'open'), ('full', 'full'), ('closed', 'closed'),
#               ('canceled', 'canceled')]
#     state = models.CharField(max_length=20, null=True, choices=states)