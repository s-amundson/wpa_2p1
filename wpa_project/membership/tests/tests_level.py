import logging
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Level

logger = logging.getLogger(__name__)


class TestsLevel(TestCase):
    fixtures = ['f1', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_level_api(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:level_api'), secure=True)
        content = json.loads(response.content)
        # messages = list(response.context['messages'])
        self.assertEqual(response.status_code, 200)

    def test_level_get(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:level'), secure=True)
        # messages = list(response.context['messages'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('membership/level.html')

    def test_level_get_existing(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:level', kwargs={'level_id': 2}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('membership/level.html')

    def test_level_post(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        d = {'name': 'Test Level', 'cost': 50, 'description': "a level for testing", 'enabled': True}

        response = self.client.post(reverse('membership:level'), d, secure=True)
        levels = Level.objects.all()
        self.assertEqual(len(levels), 5)

    def test_level_post_exists(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        d = {'name': 'Test Level', 'cost': 50, 'description': "a level for testing", 'enabled': True}

        response = self.client.post(reverse('membership:level', kwargs={'level_id': 2}), d, secure=True)
        levels = Level.objects.all()
        self.assertEqual(len(levels), 4)
