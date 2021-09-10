import logging
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

logger = logging.getLogger(__name__)


class TestsOther(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        # self.test_user = self.User.objects.get(pk=2)
        # self.client.force_login(self.test_user)

    def test_terms(self):
        self.client.get(reverse('registration:terms'), secure=True)
        self.assertTemplateUsed('registration/terms.html')

    def test_privacy(self):
        self.client.get(reverse('registration:privacy'), secure=True)
        self.assertTemplateUsed('registration/privacy.html')
