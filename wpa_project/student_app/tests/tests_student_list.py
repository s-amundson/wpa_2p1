import logging
from django.test import TestCase, Client
from django.urls import reverse

from ..models import User

logger = logging.getLogger(__name__)


class TestsSearchList(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_dict = {'first_name': '', 'last_name': '', 'safety_class': False, 'staff': False}


    def test_student_list_no_access(self):
        # Get the page, if not super or board, page is forbidden
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_list'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_student_list_access_allowed(self):
        response = self.client.get(reverse('registration:student_list'), secure=True)
        self.assertEqual(len(response.context['object_list']), 6)
        self.assertEqual(response.status_code, 200)

    def test_student_list_get_safety_class(self):
        self.test_dict['safety_class'] = True
        response = self.client.get(reverse('registration:student_list'), self.test_dict, secure=True)
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertEqual(response.status_code, 200)

    def test_student_list_get_staff(self):
        self.test_dict['staff'] = True
        response = self.client.get(reverse('registration:student_list'), self.test_dict, secure=True)
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertEqual(response.status_code, 200)

    def test_student_list_get_last_name(self):
        self.test_dict['last_name'] = 'Hoyt'
        response = self.client.get(reverse('registration:student_list'), self.test_dict, secure=True)
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['object_list'][0].id, 6)
        self.assertEqual(response.status_code, 200)

    def test_student_list_get_last_name_none(self):
        self.test_dict['last_name'] = 'Bogus'
        response = self.client.get(reverse('registration:student_list'), self.test_dict, secure=True)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(response.status_code, 200)

    def test_student_list_get_first_name(self):
        self.test_dict['first_name'] = 'Charles'
        response = self.client.get(reverse('registration:student_list'), self.test_dict, secure=True)
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['object_list'][0].id, 4)
        self.assertEqual(response.status_code, 200)

    def test_student_list_get_last_name_none(self):
        self.test_dict['first_name'] = 'Bogus'
        response = self.client.get(reverse('registration:student_list'), self.test_dict, secure=True)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(response.status_code, 200)