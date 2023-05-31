import logging
import json
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import datetime, timezone
from ..models import JoadClass, Session

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadClass(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.session_dict = {"cost": 120, "start_date": "2022-04-01", "state": "open", "student_limit": 10}
        self.class_dict = {"class_date": "2022-04-01", "session": 1, "state": "scheduled"}

    def test_user_normal_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:joad_class', kwargs={'session_id': 1}), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_board_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:joad_class', kwargs={'session_id': 1, 'class_id': 1}), secure=True)

        self.assertTemplateUsed(response, 'joad/forms/class_form.html')
        self.assertEqual(response.status_code, 200)

    def test_board_user_post_class(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:joad_class', kwargs={'session_id': 1}), self.class_dict, secure=True)
        # {'id': f.id, 'class_date': f.class_date, 'state': f.state, 'success': True}
        content = json.loads(response.content)
        logger.debug(content)
        self.assertEqual(content['id'], 6)
        self.assertEqual(content['class_date'], "2022-04-01T00:00:00-07:00")
        self.assertEqual(content['state'], 'scheduled')
        self.assertTrue(content['success'])

    def test_board_user_update_class(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        self.class_dict['class_date'] = "2022-04-04 18:00:00"

        response = self.client.post(reverse('joad:joad_class', kwargs={'session_id': 1, 'class_id': 1}),
                                    self.class_dict, secure=True)
        # {'id': f.id, 'class_date': f.class_date, 'state': f.state, 'success': True}
        content = json.loads(response.content)
        logger.debug(content)
        self.assertEqual(content['id'], 1)
        self.assertEqual(content['class_date'], "2022-04-04T18:00:00-07:00")
        self.assertEqual(content['state'], 'scheduled')
        self.assertTrue(content['success'])
        jc = JoadClass.objects.get(pk=1)
        self.assertEqual(jc.event.event_date, datetime(2022, 4, 5, 1, 0, tzinfo=timezone.utc))


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
