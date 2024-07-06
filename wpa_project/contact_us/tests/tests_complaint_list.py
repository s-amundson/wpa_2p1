import logging

from django.apps import apps
from django.test import TestCase, Client, tag
from django.urls import reverse


from ..models import Category, Message, Complaint

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsComplaintList(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def add_message(self):
        complaint = Complaint.objects.create(
            category='services',
            incident_date="2021-05-31",
            message='test message')

    # @tag('temp')
    def test_get_list_auth(self):
        self.add_message()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:complaint_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/complaint_list.html')
        self.assertEqual(len(response.context['object_list']), 1)

    # @tag('temp')
    def test_get_list_auth_empty(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:complaint_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/complaint_list.html')
        self.assertEqual(len(response.context['object_list']), 0)

    # @tag('temp')
    def test_get_list_no_auth(self):
        self.add_message()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('contact_us:message_list'), secure=True)
        self.assertEqual(response.status_code, 403)
