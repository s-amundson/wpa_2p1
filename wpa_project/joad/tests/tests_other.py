import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadOther(TestCase):
    fixtures = ['f1', 'joad1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_url = reverse('joad:student_list')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_dict = {'first_name': '', 'last_name': '', 'last_event': False}

    def test_student_list_no_access(self):
        # Get the page, if not super or board, page is forbidden
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_student_list_access_allowed(self):
        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(len(response.context['object_list']), 4)
        self.assertEqual(response.status_code, 200)

    def test_student_list_last_event(self):
        response = self.client.get(self.test_url, secure=True)
        self.test_dict['last_event'] = True
        self.assertEqual(len(response.context['object_list']), 4)
        self.assertEqual(response.status_code, 200)
