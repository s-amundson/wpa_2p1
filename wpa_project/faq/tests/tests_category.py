import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Category
logger = logging.getLogger(__name__)


class TestsCategory(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_category_detail_good(self):
        self.client.get(reverse('faq:category'), secure=True)
        self.assertTemplateUsed('contact_us/category.html')

    def test_get_category_detail_bad(self):
        self.client.force_login(self.User.objects.get(pk=3))
        response = self.client.get(reverse('faq:category'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_category_detail_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('faq:category'), secure=True)
        self.assertEqual(response.status_code, 302)

    def test_get_category_detail_id(self):
        c = Category.objects.create(title='Test Title')
        response = self.client.get(reverse('faq:category', kwargs={'category_id': c.id}), secure=True)
        self.assertTemplateUsed('contact_us/category.html')
        self.assertEqual(response.status_code, 200)

    def test_post_category_detail(self):
        response = self.client.post(reverse('faq:category'), {'title': 'Test Title'}, secure=True)
        c = Category.objects.all()
        self.assertRedirects(response, reverse('faq:category_list'))
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0].title, 'Test Title')

    def test_get_category_list(self):
        self.client.get(reverse('faq:category_list'), secure=True)
        self.assertTemplateUsed('faq/category_list.html')

    def test_get_category_list_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('faq:category_list'), secure=True)
        self.assertEqual(response.status_code, 302)

    def test_post_category_delete(self):
        c = Category.objects.create(title='Test Title')
        response = self.client.post(reverse('faq:category_delete', kwargs={'category_id': c.id}), secure=True)
        self.assertRedirects(response, reverse('faq:category_list'))
        c = Category.objects.all()
        self.assertEqual(len(c), 0)
