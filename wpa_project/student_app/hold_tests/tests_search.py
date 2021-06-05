import logging

from django.test import TestCase, Client
from django.urls import reverse

from ..models import BeginnerClass, ClassRegistration, User

logger = logging.getLogger(__name__)


class TestsClassSearch(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=2)

    def test_class_search(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:search'))
        self.assertEqual(response.status_code, 403)

        # Change user then Get the page
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/student_search.html')

        # search by email with result
        response = self.client.post(reverse('registration:search'), {'email': 'CharlesNWells@einrot.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/search_result.html')

        # search by email without result
        response = self.client.post(reverse('registration:search'), {'email': 'NoEmailFound@einrot.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/message.html')

        # search by name with result
        response = self.client.post(reverse('registration:search'), {'first_name': 'Charles', 'last_name': 'Wells'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/search_result.html')

        # search by email without result
        response = self.client.post(reverse('registration:search'), {'first_name': 'No', 'last_name': 'Body'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/message.html')

        # search by phone with result
        response = self.client.post(reverse('registration:search'), {'phone': '850-983-9979'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/search_result.html')

        # search by phone without result
        response = self.client.post(reverse('registration:search'), {'phone': '19009009999'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/message.html')

        # somehow post without search criteria
        response = self.client.post(reverse('registration:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/student_search.html')
