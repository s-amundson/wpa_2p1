import logging
import json
from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase, Client, tag
from django.urls import reverse
from ..models import User
logger = logging.getLogger(__name__)

# @tag('temp')
class TestsInstructor(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_form(self):
        # Get the page, if not instructor, page is forbidden
        response = self.client.get(reverse('registration:instructor_update'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/forms/instructor_form.html')

    # @tag('temp')
    def test_get_non_instructor(self):
        self.test_user = User.objects.get(pk=2)
        self.test_user.groups.remove(Group.objects.get(name='instructors'))
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:instructor_update'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_post_form(self):
        response = self.client.post(reverse('registration:instructor_update'),
                                   {'instructor_expire_date': '2022-11-21', 'instructor_level': 2},
                                   secure=True)
        self.test_user = User.objects.get(pk=1)
        self.assertEqual(self.test_user.instructor_expire_date, date(2022, 11, 21))

    # @tag('temp')
    def test_post_form_error(self):
        response = self.client.post(reverse('registration:instructor_update'),
                                   {'instructor_expire_date': '2022', 'instructor_level': 2},
                                   secure=True)
        self.test_user = User.objects.get(pk=1)
        content = json.loads(response.content)
        self.assertEqual(content['status'], 'error')

    # @tag('temp')
    def test_post_non_instructor(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        self.test_user.groups.remove(Group.objects.get(name='instructors'))
        response = self.client.post(reverse('registration:instructor_update'),
                                   {'instructor_expire_date': '2022-11-21', 'instructor_level': 2},
                                   secure=True)
        self.test_user = User.objects.get(pk=2)
        self.assertEqual(self.test_user.instructor_expire_date, None)
