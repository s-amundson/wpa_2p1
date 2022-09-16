import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

logger = logging.getLogger(__name__)


class TestsPost(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_posts_good(self):
        self.client.get(reverse('facebook:posts'), secure=True)
        self.assertTemplateUsed('facebook/post_list.html')

    def test_get_posts_insert_good(self):
        self.client.get(reverse('facebook:posts_include'), secure=True)
        self.assertTemplateUsed('facebook/post_list_insert.html')
