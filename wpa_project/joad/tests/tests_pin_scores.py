import logging

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from ..models import PinScores

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsPinScores(TestCase):
    # fixtures = ['f1', 'f2', 'f3']
    fixtures = ['f1', 'pinscores']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.post_dict = {'bow': 'barebow', 'category': 'joad_indoor', 'distance': 9, 'target': 60, 'score': 45,
                          'stars': 1}
        self.pin_score_count = 52
        # self.test_user = User.objects.get(pk=1)
        # self.client.force_login(self.test_user)

    def test_get_pin_score_list_auth(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('joad:pin_score_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        logging.debug(len(response.context['object_list']))
        self.assertEqual(len(response.context['object_list']), self.pin_score_count)
        # context = self.client.request.

    def test_get_pin_score_list_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('joad:pin_score_list'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_pin_score_get_auth(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('joad:pin_score'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/form_as_p.html')

    def test_pin_score_get_auth_existing(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('joad:pin_score', kwargs={'score_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/form_as_p.html')

    def test_get_pin_score_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('joad:pin_score'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_post_pin_score_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('joad:pin_score_list'), self.post_dict, secure=True)
        self.assertEqual(response.status_code, 403)
        ps = PinScores.objects.all()
        self.assertEqual(len(ps), self.pin_score_count)

    def test_post_pin_score_auth_new(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('joad:pin_score'), self.post_dict, secure=True)
        # self.assertEqual(response.status_code, 403)
        ps = PinScores.objects.all()
        self.assertEqual(len(ps), self.pin_score_count + 1)
        self.assertRedirects(response, reverse('joad:pin_score_list'), 302)

    def test_post_pin_score_auth_update(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('joad:pin_score', kwargs={'score_id': 1}), self.post_dict, secure=True)
        # self.assertEqual(response.status_code, 403)
        ps = PinScores.objects.all()
        self.assertEqual(len(ps), self.pin_score_count)
        self.assertRedirects(response, reverse('joad:pin_score_list'), 302)
