import json
import logging
from django.test import TestCase, Client
from django.urls import reverse

from ..models import User

logger = logging.getLogger(__name__)


class TestsTheme(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    # def test_get_theme(self):
    #     # Get the page, if not super or board, page is forbidden
    #     response = self.client.get(reverse('registration:theme'), secure=True)
    #     self.assertEqual(response.status_code, 404)

    def test_post_good(self):
        response = self.client.post(reverse('registration:theme'), {'theme': False, }, secure=True)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        logging.debug(content)
        self.assertEqual(content['status'], 'SUCCESS')
        u = User.objects.get(pk=1)
        self.assertFalse(u.dark_theme)

    def test_post_error(self):
        response = self.client.post(reverse('registration:theme'), {'theme': 'dark', }, secure=True)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        logging.debug(content)
        self.assertEqual(content['theme'], ['Must be a valid boolean.'])
        u = User.objects.get(pk=1)
        self.assertTrue(u.dark_theme)
