import logging
import json
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from ..models import JoadEvent, EventRegistration

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadEventRegistration(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_user_normal_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:event_registration'), secure=True)
        self.assertTemplateUsed(response, 'joad/event_registration.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['form'].fields), 1)

    def test_board_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:event_registration'), secure=True)
        self.assertTemplateUsed(response, 'joad/event_registration.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['form'].fields), 5)

    # def test_student_post(self):
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 1}),
    #                                 {'event': 1, 'student_5': 'on'}, secure=True)
    #     self.assertEqual(response.status_code, 200)
    #     events = EventRegistration.objects.all()
    #     self.assertEqual(len(events), 2)
