import logging

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

from event.models import Event, Registration, RegistrationAdmin
from student_app.models import Student

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsLogs(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.url = reverse('programs:class_registration_admin_list')

    def test_user_normal_user_not_authorized(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_board_get_empty(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)

    def test_board_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        ncr = Registration.objects.create(
            event=Event.objects.get(pk=1),
            student=Student.objects.get(pk=4),
            pay_status='admin',
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f")
        note = 'test note'
        cra = RegistrationAdmin.objects.create(class_registration=ncr, staff=self.test_user, note=note)

        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 1)

