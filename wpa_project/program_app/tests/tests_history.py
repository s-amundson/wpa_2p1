import logging
import uuid
import json

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import BeginnerClass, ClassRegistration
Student = apps.get_model('student_app', 'Student')
User = apps.get_model('student_app', 'User')
logger = logging.getLogger(__name__)


class TestsAttendanceHistory(TestCase):
    fixtures = ['f1', 'f3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_no_user_get(self):
        # allow user to access
        response = self.client.get(reverse('programs:history'), secure=True)
        self.assertRedirects(response, '/accounts/login/?next=/programs/history/')

    def test_user_get(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('programs:history'), secure=True)
        self.assertTemplateUsed(response, 'program_app/history.html')
        self.assertEqual(response.status_code, 200)