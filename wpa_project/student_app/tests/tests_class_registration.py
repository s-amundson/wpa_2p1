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

class TestsClassRegistration(TestCase):
    fixtures = ['f1']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User(email='ChristyCSnow@gustr.com', password='password', first_name='Christy',
                              last_name='Snow', is_active=True)
        self.test_user.save()
        logging.debug('here')

    def test_beginner_class(self):
        # Get the page
        self.client.force_login(self.test_user)
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
