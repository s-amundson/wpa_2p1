import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

from ..models import Level, Membership, Member
from student_app.models import Student
logger = logging.getLogger(__name__)


class TestsMemberList(TestCase):
    fixtures = ['f1', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')
        self.test_url = reverse('membership:member_list')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.post_dict = {'query_date': '2022-09-01', 'order_by': 'last', 'csv_export': False}

    def test_member_list_get_page(self):
        # Get the page, if not super or board, page is forbidden
        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(response.status_code, 200)

    def test_member_list_get_page_bad(self):
        self.client.force_login(self.User.objects.get(pk=2))
        response = self.client.get(self.test_url, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_member_list_get_data_normal(self):
        response = self.client.get(self.test_url, self.post_dict, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'membership/member_list.html')

    def test_member_list_get_data_csv(self):
        self.post_dict['csv_export'] = True
        response = self.client.get(self.test_url, self.post_dict, secure=True)
        self.assertEqual(response.status_code, 200)
