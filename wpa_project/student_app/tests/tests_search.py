import logging
from django.test import TestCase, Client, tag
from django.urls import reverse

from ..models import User

logger = logging.getLogger(__name__)

# @tag('temp')
class TestsSearch(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.success_url = reverse('registration:search_result_list')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_search_forbidden(self):
        # Get the page, if not super or staff, page is forbidden
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:search'), secure=True)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('registration:search'), {'email': 'CharlesNWells@einrot.com'}, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_search(self):
        response = self.client.get(reverse('registration:search'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/student_search.html')

        # search by email with result
        response = self.client.post(reverse('registration:search'), {'email': 'CharlesNWells@einrot.com'}, secure=True)
        self.assertRedirects(response, self.success_url)
        # self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed('student_app/search_result.html')

        # search by email without result
        response = self.client.post(reverse('registration:search'), {'email': 'NoEmailFound@einrot.com'}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/student_search.html')

        # search by name with result
        response = self.client.post(reverse('registration:search_name'), {'first_name': 'Charles', 'last_name': 'Wells'}, secure=True)
        self.assertRedirects(response, self.success_url)

        # search by email without result
        response = self.client.post(reverse('registration:search_name'), {'first_name': 'No', 'last_name': 'Body'}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/student_search.html')

        # search by phone with result
        response = self.client.post(reverse('registration:search_phone'), {'phone': '850-983-9979'}, secure=True)
        self.assertRedirects(response, self.success_url)

        # search by phone without result
        response = self.client.post(reverse('registration:search_phone'), {'phone': '19009009999'}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/student_search.html')

        # somehow post without search criteria
        response = self.client.post(reverse('registration:search'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/student_search.html')

    def test_search_result_get_auth(self):
        response = self.client.get(reverse('registration:search_result', kwargs={'student_family': 2}), secure=True)
        self.assertTemplateUsed('student_app/search_result.html')
        self.assertEqual(response.status_code, 200)

    def test_search_result_get_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:search_result', kwargs={'student_family': 2}), secure=True)
        self.assertTemplateUsed('student_app/search_result.html')
        self.assertEqual(response.status_code, 403)

    def test_search_result_list_get_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:search_result_list'), secure=True)
        self.assertTemplateUsed('student_app/search_result.html')
        self.assertEqual(response.status_code, 403)
