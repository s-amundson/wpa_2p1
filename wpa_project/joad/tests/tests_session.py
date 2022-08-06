import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Session, Registration
from student_app.models import Student

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadSession(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.session_dict = {"cost": 125, "start_date": "2022-04-01", "state": "open", "student_limit": 10}
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
        self.assertEqual(response.status_code, 200)

    def test_board_user_get_existing(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:session', kwargs={'session_id': 1}), secure=True)
        self.assertIsNotNone(response.context['session_id'])
        # self.assertEqual(len(response.context['object_list']), 3)
        self.assertEqual(response.status_code, 200)

    def test_board_user_post_session(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:session'), self.session_dict, secure=True)
        s = Session.objects.all()
        self.assertEqual(len(s), 3)
        self.assertEqual(response.status_code, 302)

    def test_board_user_post_existing(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.post(reverse('joad:session', kwargs={'session_id': 1}), self.session_dict, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_get_session_status(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('joad:session_status', kwargs={'session_id': 1}), secure=True)
        self.assertEqual(response.context['cost'], 125)
        self.assertEqual(response.context['limit'], 10)
        self.assertEqual(response.context['openings'], 10)

    def test_get_session_status2(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        registration = Registration.objects.create(
            pay_status='paid',
            idempotency_key='992c77a8-87cc-45af-b390-13d80554e3e0',
            student=Student.objects.get(pk=9),
            session=Session.objects.get(pk=1))

        response = self.client.get(reverse('joad:session_status', kwargs={'session_id': 1}), secure=True)
        self.assertEqual(response.context['cost'], 125)
        self.assertEqual(response.context['limit'], 10)
        self.assertEqual(response.context['openings'], 9)

    def test_get_states(self):
        self.assertEqual(Session().get_states(), ['scheduled', 'open', 'full', 'closed', 'canceled', 'recorded'])