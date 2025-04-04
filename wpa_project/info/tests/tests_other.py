import logging
from django.test import TestCase, Client, tag
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

    # @tag('temp')
    def test_info(self):
        items = ['about', 'by-laws', 'class_description', 'constitution', 'directions']
        for item in items:
            self.client.get(reverse('information:info', kwargs={'info': item}), secure=True)
            self.assertTemplateUsed(f'info/info.html')

    # @tag('temp')
    def test_info_no_exist(self):
        response = self.client.get(reverse('information:info', kwargs={'info': 'no exist'}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
