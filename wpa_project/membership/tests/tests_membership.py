import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Membership

logger = logging.getLogger(__name__)


class TestsMembership(TestCase):
    fixtures = ['f1', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_membership_get_page(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:membership'), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_membership_to_old(self):
        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'level': '2'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

    def test_membership_good(self):
        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'level': '1'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['payment_db'][1], 'Membership')

    def test_membership_to_young(self):
        Student = apps.get_model(app_label='student_app', model_name='Student')
        s = Student.objects.get(pk=2)
        s.dob = "2011-07-22"
        s.save()

        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'level': '1'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

    def test_membership_family(self):
        response = self.client.post(reverse('membership:membership'), {'student_2': 'on', 'student_3': 'on', 'level': '3'},
                                    secure=True)
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['payment_db'][1], 'Membership')

    def test_membership_no_student(self):
        response = self.client.post(reverse('membership:membership'), {'level': '3'}, secure=True)
        # self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
