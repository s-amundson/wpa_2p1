import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from ..models import Card, PaymentLog

logger = logging.getLogger(__name__)
User = get_user_model()


class TestsReport(TestCase):
    fixtures = ['f1', 'square_1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.post_dict = {'beginning_date': '2022-02-02', 'end_date': '2022-06-06'}
        self.url = reverse('payment:report')


    def test_get_report(self):
        response = self.client.get(self.url, secure=True)
        self.assertTemplateUsed(response, 'payment/report.html')

    def test_get_report_bad(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_post_good(self):
        response = self.client.post(self.url, self.post_dict, secure=True)
        self.assertTemplateUsed(response, 'payment/report.html')