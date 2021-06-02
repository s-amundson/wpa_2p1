import json
import logging
import os

import allauth
from django.conf import settings
from django.template.loader import render_to_string
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import auth

from ..models import StudentFamily, Student, User

logger = logging.getLogger(__name__)

class RegisterStudent(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User(email='ChristyCSnow@gustr.com', first_name='Christy',
                              last_name='Snow', is_active=True)
        self.test_user.set_password('password')
        self.test_user.save()
        logging.debug('here')

    def test_login_required(self):
        def get_page(page, target):
            response = self.client.get(reverse(page))
            self.assertRedirects(response, f'/accounts/login/?next=/{target}')

        get_page('registration:profile', 'profile')
        get_page('registration:student_register', 'student_register')
        get_page('registration:add_student', 'add_student')

    def test_register(self):
        # if student hasn't registered. we need to send them to registration starting with address
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:profile'))
        self.assertRedirects(response, reverse('registration:student_register'))

        # add a student family
        d = {'street': '123 main', 'city': 'city', 'state': 'ca', 'post_code': 12345, 'phone': '123.123.1234'}
        response = self.client.post(reverse('registration:student_register'), d)
        self.assertTemplateUsed('student_app/profile.html')
        self.assertRedirects(response, reverse('registration:profile'))
        sf = StudentFamily.objects.all()
        self.assertEquals(len(sf), 1)

        # check that we can go back to profile.
        response = self.client.get(reverse('registration:profile'))
        self.assertEqual(response.status_code, 200)

        # add a student
        d = {'first_name':'Christy', 'last_name': 'Smith', 'dob': '2020-02-02'}
        response = self.client.post(reverse('registration:add_student'), d)
        # self.assertEqual(response.status_code, 200)
        s = sf[0].student_set.all()
        logging.debug(s)
        self.assertEquals(len(s), 1)

    def test_login_invaid(self):
        """Tests invalid login with username and password"""
        response = self.client.post(reverse('account_login'), {'login': 'john', 'password': 'smith'})
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.assertTemplateUsed('account/login.html')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_login'), {'login': 'john@smith.com', 'password': 'smith'})
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.assertTemplateUsed('account/login.html')
        self.assertEqual(response.status_code, 200)
        # self.assertRedirects(reverse('account_login'))
        # with :
        #     render_to_string('account/login.html')
        logging.debug(response)

    # def test_login_valid(self):
    #     logging.debug(self.test_user.email)
    #     response = self.client.post(reverse('account_login'),
    #                                 {'login': self.test_user.email, 'password': self.test_user.password})
    #     user = auth.get_user(self.client)
    #     # logging.debug(self.client.)
    #     self.assertTrue(user.is_authenticated)
    #     self.assertTemplateUsed('account/login.html')
    #     self.assertEqual(response.status_code, 200)

