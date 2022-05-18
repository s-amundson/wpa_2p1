import logging
import json
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from ..models import JoadEvent, EventRegistration

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadEvent(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.event_dict = {"cost": 15, 'event_date': "2022-02-15 16:00:00", 'event_type': 'joad_indoor',
                           'state': 'open', 'student_limit': 20, 'pin_cost': 5}

    def test_user_normal_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:event'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_board_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:event'), secure=True)

        self.assertTemplateUsed(response, 'joad/event.html')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['student_list']), 0)

    def test_board_user_get_event(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:event', kwargs={'event_id': 1}), secure=True)

        self.assertTemplateUsed(response, 'joad/event.html')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['student_list']), 1)

    def test_board_user_post_event(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event'), self.event_dict, secure=True)
        event = JoadEvent.objects.all()
        self.assertEqual(len(event), 2)

    def test_board_user_post_event_invalid(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        del self.event_dict['event_date']

        response = self.client.post(reverse('joad:event'), self.event_dict, secure=True)
        event = JoadEvent.objects.all()
        self.assertEqual(len(event), 1)
        self.assertContains(response, 'This field is required.')

class TestsJoadClassList(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_board_user_get_no_class(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:class_list'), secure=True)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertTemplateUsed(response, 'joad/tables/class_table.html')
        self.assertEqual(response.status_code, 200)

    def test_board_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:class_list', kwargs={'session_id': 1}), secure=True)
        self.assertEqual(len(response.context['object_list']), 3)
        self.assertTemplateUsed(response, 'joad/tables/class_table.html')
        self.assertEqual(response.status_code, 200)

    def test_board_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:class_list', kwargs={'session_id': 1}), secure=True)
        self.assertEqual(len(response.context['object_list']), 3)
        self.assertTemplateUsed(response, 'joad/tables/class_table.html')
        self.assertEqual(response.status_code, 200)

    def test_board_user_get_all_sessions(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:class_list', kwargs={'session_id': 0}), secure=True)
        self.assertEqual(len(response.context['object_list']), 5)
        self.assertTemplateUsed(response, 'joad/tables/class_table.html')
        self.assertEqual(response.status_code, 200)
