import logging
import json
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Student


logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsCovidVax(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.student_dict = {'session': 1, 'student_5': True}

    def test_user_none_post(self):
        response = self.client.post(reverse('registration:covid_vax', kwargs={'student_id': 5}), {'covid_vax_5': True}, secure=True)
        s = Student.objects.get(pk=5)
        self.assertFalse(s.covid_vax)
        self.assertEqual(response.status_code, 302)

    def test_user_normal_post(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('registration:covid_vax', kwargs={'student_id': 5}), {'covid_vax_5': True}, secure=True)
        s = Student.objects.get(pk=5)
        self.assertFalse(s.covid_vax)
        self.assertEqual(response.status_code, 403)

    def test_staff_user_post_vax(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('registration:covid_vax', kwargs={'student_id': 5}), {'covid_vax_5': True}, secure=True)
        s = Student.objects.get(pk=5)
        self.assertTrue(s.covid_vax)
        content = json.loads(response.content)
        self.assertFalse(content['error'])

    def test_staff_user_post_unattend(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        s = Student.objects.get(pk=5)
        s.covid_vax = True
        s.save()

        response = self.client.post(reverse('registration:covid_vax', kwargs={'student_id': 5}), {'covid_vax_5': False}, secure=True)
        rs = Student.objects.get(pk=5)
        self.assertFalse(rs.covid_vax)
        content = json.loads(response.content)
        self.assertFalse(content['error'])

    def test_staff_user_post_error(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('registration:covid_vax', kwargs={'student_id': 5}), secure=True)
        s = Student.objects.get(pk=5)
        self.assertFalse(s.covid_vax)
        content = json.loads(response.content)
        self.assertTrue(content['error'])
