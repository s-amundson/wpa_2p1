import logging

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse


logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsCalendar(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_UID = 3

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        logging.debug('here')

    def test_get_calendar(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('programs:class_calendar'), secure=True)
        self.assertEqual(response.status_code, 200)
