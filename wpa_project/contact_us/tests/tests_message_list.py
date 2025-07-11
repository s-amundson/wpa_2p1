import logging

from django.apps import apps
from django.test import TestCase, Client, tag
from django.urls import reverse


from ..models import Category, Message

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


# @tag('temp')
class TestsMessageList(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.post_dict = {'contact_name': ['Emily Conlan'], 'email': ['EmilyNConlan@einrot.com'], 'category': ['2'],
                          'message': ['test message']}

    def add_message(self):
        c = Category.objects.create(title='test category', email='none@example.com')
        message = Message.objects.create(category=c,
                                         contact_name=self.post_dict['contact_name'][0],
                                         email=self.post_dict['email'][0],
                                         message=self.post_dict['message'][0])

    # @tag('temp')
    def test_get_list_auth(self):
        self.add_message()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:message_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message_list.html')
        self.assertEqual(len(response.context['object_list']), 1)

    # @tag('temp')
    def test_get_list_auth_empty(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:message_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/message_list.html')
        self.assertEqual(len(response.context['object_list']), 0)

    def test_get_list_no_auth(self):
        self.add_message()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:message_list'), secure=True)
        self.assertEqual(response.status_code, 403)
