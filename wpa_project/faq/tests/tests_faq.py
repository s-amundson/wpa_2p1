import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Category, Faq
logger = logging.getLogger(__name__)


class TestsFaq(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_faq_edit_good(self):
        self.client.get(reverse('faq:edit'), secure=True)
        self.assertTemplateUsed('student_app/form_as_p.html')

    def test_get_faq_edit_bad(self):
        self.client.force_login(self.User.objects.get(pk=3))
        response = self.client.get(reverse('faq:edit'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_faq_edit_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('faq:edit'), secure=True)
        self.assertEqual(response.status_code, 302)

    def test_get_faq_edit_id(self):
        c = Category.objects.create(title='Test Title')
        f = Faq.objects.create(question='test question', answer='test answer', status=1)
        f.category.add(c)
        response = self.client.get(reverse('faq:edit', kwargs={'faq_id': f.id}), secure=True)
        self.assertTemplateUsed('student_app/form_as_p.html')
        self.assertEqual(response.status_code, 200)

    def test_post_faq_detail(self):
        c = Category.objects.create(title='Test Title')
        d = {'category': c.id, 'question': 'test question', 'answer': 'test answer', 'status': 1}
        response = self.client.post(reverse('faq:edit'), d, secure=True)
        f = Faq.objects.all()
        self.assertRedirects(response, reverse('faq:faq'))
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].question, 'test question')

    def test_get_faq_list(self):
        self.client.get(reverse('faq:faq'), secure=True)
        self.assertTemplateUsed('faq/faq_list.html')
