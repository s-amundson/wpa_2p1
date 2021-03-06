import logging
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

    def test_policy_privacy(self):
        self.client.get(reverse('registration:policy', kwargs={'policy': 'privacy'}), secure=True)
        self.assertTemplateUsed('registration/privacy.html')

    def test_policy_covid(self):
        self.client.get(reverse('registration:policy', kwargs={'policy': 'covid'}), secure=True)
        self.assertTemplateUsed('registration/covid_policy.html')

    def test_policy_invalid(self):
        response = self.client.get(reverse('registration:policy', kwargs={'policy': 'invalid'}), secure=True)
        self.assertEqual(response.status_code, 404)
