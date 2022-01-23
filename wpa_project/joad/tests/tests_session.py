import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Session

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadSession(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.session_dict = {"cost": 120, "start_date": "2022-04-01", "state": "open", "student_limit": 10}
        self.class_dict = {"class_date": "2022-04-01", "session": 1, "state": "scheduled"}

    def test_user_normal_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.get(reverse('joad:session'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_board_user_get(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:session'), secure=True)
        self.assertIsNone(response.context['session_id'])
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(response.status_code, 200)

    def test_board_user_post_session(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:session'), self.session_dict, secure=True)
        s = Session.objects.all()
        self.assertEqual(len(s), 2)
        self.assertEqual(response.status_code, 200)
