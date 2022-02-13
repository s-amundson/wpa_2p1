import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail

from ..models import Category, Message
logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsMessage(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.post_dict = {'contact_name': ['Emily Conlan'], 'email': ['EmilyNConlan@einrot.com'], 'category': ['2'],
                          'message': ['test message']}

    def _category_post(self):
        c = Category.objects.create(title='test category')
        c.recipients.set([self.test_user])
        self.post_dict['category'] = c.id

    def check_email(self):
        self.assertEqual(mail.outbox[0].subject, 'WPA Contact Us test category')
        self.assertTrue(mail.outbox[0].body.find('test message') > 0)

    def test_get_message_user(self):
        response = self.client.get(reverse('contact_us:contact'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message.html')

    def test_get_message_nonuser(self):
        self.client.logout()
        response = self.client.get(reverse('contact_us:contact'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message.html')

    def test_post_message_user(self):
        self._category_post()
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()

        self.assertEqual(len(message), 1)
        self.check_email()

    def test_post_message_nonuser(self):
        self.client.logout()
        self._category_post()
        response = self.client.post(reverse('contact_us:contact'), self.post_dict, secure=True)
        message = Message.objects.all()
        self.assertEqual(len(message), 1)
        self.check_email()
