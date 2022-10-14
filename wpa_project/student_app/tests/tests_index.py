import logging
from django.test import TestCase, Client
from django.urls import reverse
from ..models import User
from contact_us.models import Email
logger = logging.getLogger(__name__)


class TestsIndex(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_get_index(self):
        response = self.client.get(reverse('registration:index'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/index.html')

    def test_get_index_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:index'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/index.html')

    def test_get_signup(self):
        response = self.client.get(reverse('account_signup'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('account/signup.html')

    def test_post_signup(self):
        d = {"email": 'sam@example.com', "password1": "johndoe",  "password2": "johndoe"}
        response = self.client.post(reverse('account_signup'), d, secure=True)
        self.assertEqual(response.status_code, 200)
        e = Email.objects.all()
        self.assertEqual(e.count(), 0)
