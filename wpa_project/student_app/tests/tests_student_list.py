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

    def test_student_list_no_access(self):
        # Get the page, if not super or board, page is forbidden
        self.test_user = User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('registration:student_list'), secure=True)
        self.assertEqual(response.status_code, 403)


    def test_student_list_access_allowed(self):
        response = self.client.get(reverse('registration:student_list'), secure=True)
        self.assertEqual(response.status_code, 200)



