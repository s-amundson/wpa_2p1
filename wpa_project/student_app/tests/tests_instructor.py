import logging
from datetime import date

from django.test import TestCase, Client
from django.urls import reverse
from ..models import User
logger = logging.getLogger(__name__)


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

    def test_get_non_instructor(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:instructor_update'), secure=True)
        self.assertEqual(response.status_code, 404)

    def test_post_form(self):
        response = self.client.post(reverse('registration:instructor_update'),
                                   {'instructor_expire_date': '2022-11-21'},
                                   secure=True)
        self.test_user = User.objects.get(pk=1)
        self.assertEqual(self.test_user.instructor_expire_date, date(2022, 11, 21))

    def test_post_non_instructor(self):
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('registration:instructor_update'),
                                   {'instructor_expire_date': '2022-11-21'},
                                   secure=True)
        self.test_user = User.objects.get(pk=2)
        self.assertEqual(self.test_user.instructor_expire_date, None)
