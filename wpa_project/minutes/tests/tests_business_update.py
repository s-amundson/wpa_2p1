import logging
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Minutes, Business, BusinessUpdate, Report

logger = logging.getLogger(__name__)


class TestsBusinessUpdate(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_business_update(self):
        response = self.client.get(reverse('minutes:business_update'), secure=True)
        self.assertTemplateUsed('minutes/forms/business_update_form.html')

    def test_get_business_update_existing(self):
        b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
        b1.save()
        bu = BusinessUpdate(business=b1, update_date='2021-09-04', update_text="test update")
        bu.save()

        response = self.client.get(reverse('minutes:business_update', kwargs={'update_id': bu.id}), secure=True)
        self.assertTemplateUsed('minutes/forms/business_update_form.html')


    def test_post_business_update_new(self):
        b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
        b1.save()

        d = {'business': b1.id, 'update_text': "test business text"}
        response = self.client.post(reverse('minutes:business_update'), d, secure=True)
        b = BusinessUpdate.objects.last()
        self.assertEqual(len(BusinessUpdate.objects.all()), 1)
        self.assertEqual(b.update_text, "test business text")

    def test_post_business_update_existing(self):
        b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
        b1.save()
        bu = BusinessUpdate(business=b1, update_date='2021-09-04', update_text="test update")
        bu.save()

        d = {'business': b1.id, 'update_text': "test business text"}
        response = self.client.post(reverse('minutes:business_update', kwargs={'update_id': bu.id}),
                                    d, secure=True)
        b = BusinessUpdate.objects.last()
        self.assertEqual(len(BusinessUpdate.objects.all()), 1)
        self.assertEqual(b.update_text, "test business text")
