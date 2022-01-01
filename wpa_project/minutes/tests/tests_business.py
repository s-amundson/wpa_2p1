import logging
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Minutes, Business, BusinessUpdate, Report

logger = logging.getLogger(__name__)


class TestsBusiness(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    # def test_get_business(self):
    #     response = self.client.get(reverse('minutes:business'), secure=True)
    #     self.assertTemplateUsed('minutes/forms/business_form.html')

    # def test_get_business_existing(self):
    #     b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
    #     b1.save()
    #
    #     response = self.client.get(reverse('minutes:business', kwargs={'business_id': b1.id}), secure=True)
    #     self.assertTemplateUsed('minutes/forms/business_form.html')
    #
    def test_post_business_new(self):
        d = {'business': "test business text", 'resolved_bool': False}
        response = self.client.post(reverse('minutes:business'), d, secure=True)
        b = Business.objects.last()
        self.assertEqual(len(Business.objects.all()), 1)
        self.assertEqual(b.business, "test business text")

    def test_post_business_existing(self):
        b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
        b1.save()

        d = {'business': "test business text", 'resolved_bool': False}
        response = self.client.post(reverse('minutes:business', kwargs={'business_id': b1.id}), d, secure=True)
        b = Business.objects.last()
        self.assertEqual(len(Business.objects.all()), 1)
        self.assertEqual(b.business, "test business text")

    def test_post_business_existing_resolved(self):
        b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
        b1.save()
        self.assertIsNone(b1.resolved)
        d = {'business': "test business text", 'resolved_bool': True}
        response = self.client.post(reverse('minutes:business', kwargs={'business_id': b1.id}), d, secure=True)
        b = Business.objects.last()
        self.assertEqual(len(Business.objects.all()), 1)
        self.assertEqual(b.business, "test business text")
        self.assertIsNotNone(b.resolved)

    def test_post_business_existing_unresolved(self):
        b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business', resolved='2021-09-04')
        b1.save()
        self.assertIsNotNone(b1.resolved)
        d = {'business': "test business text", 'resolved_bool': False}
        response = self.client.post(reverse('minutes:business', kwargs={'business_id': b1.id}), d, secure=True)
        b = Business.objects.last()
        self.assertEqual(len(Business.objects.all()), 1)
        self.assertEqual(b.business, "test business text")
        self.assertIsNone(b.resolved)
