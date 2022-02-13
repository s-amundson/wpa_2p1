import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Category
logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsCategory(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_delete_category(self):
        c = Category.objects.create(title='test category')
        c.recipients.set([self.test_user])

        response = self.client.post(reverse('contact_us:delete_category', kwargs={'category_id': c.id}), secure=True)
        self.assertRedirects(response, reverse('contact_us:category_list'))
        c = Category.objects.all()
        self.assertEqual(len(c), 0)

    def test_delete_category_invalid(self):
        c = Category.objects.create(title='test category')
        c.recipients.set([self.test_user])

        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('contact_us:delete_category', kwargs={'category_id': c.id}), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_category_list_get(self):
        c = Category.objects.create(title='test category')
        c.recipients.set([self.test_user])
        response = self.client.get(reverse('contact_us:category_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 1)

    def test_category_list_get_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        c = Category.objects.create(title='test category')
        c.recipients.set([self.test_user])
        response = self.client.get(reverse('contact_us:category_list'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_category_view_get_auth(self):
        response = self.client.get(reverse('contact_us:category'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message.html')

    def test_category_view_get_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:category'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_category_view_post_auth(self):
        post_dict = {'title': ['Events'], 'recipients': ['1']}
        response = self.client.post(reverse('contact_us:category'), post_dict, secure=True)
        self.assertRedirects(response, reverse('contact_us:category_list'))

    def test_category_view_post_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('contact_us:category'), secure=True)
        self.assertEqual(response.status_code, 403)
