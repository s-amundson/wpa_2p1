import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

from student_app.models import Student

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadIndex(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_user_normal_no_student(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], False)
        self.assertEqual(len(response.context['students']), 0)
        self.assertEqual(response.status_code, 200)

    def test_staff_user_no_student(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], True)
        self.assertEqual(len(response.context['students']), 0)
        self.assertEqual(response.status_code, 200)

    def test_user_normal_not_joad(self):
        student = Student.objects.get(pk=5)
        student.dob = "1982-11-28"
        student.save()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], False)
        self.assertEqual(len(response.context['students']), 0)
        self.assertEqual(response.status_code, 200)

    def test_user_normal_is_joad(self):
        student = Student.objects.get(pk=5)
        student.dob = "1982-11-28"
        student.save()
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], True)
        self.assertEqual(len(response.context['students']), 1)
        self.assertEqual(response.status_code, 200)
