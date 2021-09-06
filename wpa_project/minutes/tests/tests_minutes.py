import logging
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Minutes, Business, BusinessUpdate, Report

logger = logging.getLogger(__name__)


class TestsMinutes(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_minutes_list(self):
        # Get the page, if not super or board, page is forbidden
        response = self.client.get(reverse('minutes:minutes_list'), secure=True)
        self.assertTemplateUsed('minutes/minutes_list.html')

    def test_get_minutes_form_new(self):
        response = self.client.get(reverse('minutes:minutes_form'), secure=True)
        self.assertIsNone(response.context['minutes_id'])
        logging.debug(response.context)
        self.assertTemplateUsed('minutes/minutes_form.html')

    def test_get_minutes_form_unauthorized(self):
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('minutes:minutes_form'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_minutes_form_old(self):
        m = Minutes(
            meeting_date='2021-09-04', start_time='19:30', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()
        logging.debug(m)

        r = Report(report='Test Report', minutes=m, owner='president')
        r.save()
        b1 = Business(minutes=None, added_date='2021-08-04', business='Some old test business')
        b1.save()
        logging.debug(b1)
        b2 = Business(minutes=m, added_date='2021-09-04', business='new test business')
        b2.save()
        bu = BusinessUpdate(business=b1, update_date='2021-09-04', update_text="test update")
        bu.save()

        response = self.client.get(reverse('minutes:minutes_form', kwargs={'minutes_id': m.id}), secure=True)

        self.assertEqual(response.context['minutes_id'], 1)
        self.assertEqual(len(response.context['reports']['president']), 1)
        self.assertEqual(len(response.context['reports']['vice']), 0)
        self.assertEqual(len(response.context['old_business']), 1)
        self.assertEqual(len(response.context['old_business'][0]['updates']), 1)

    def test_post_minutes_form_unauthorized(self):
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('minutes:minutes_form'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_post_minutes_from_new(self):
        d = {'meeting_date': '2021-09-04', 'start_time': '19:30', 'memberships': 0}
        response = self.client.post(reverse('minutes:minutes_form'), d, secure=True)
        m = Minutes.objects.all()
        self.assertEqual(len(m), 1)

    def test_post_minutes_form_old(self):
        m = Minutes(
            meeting_date='2021-09-04', start_time='19:30', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()
        logging.debug(m)

        r = Report(report='Test Report', minutes=m, owner='president')
        r.save()
        b1 = Business(minutes=None, added_date='2021-08-04', business='Some old test business')
        b1.save()
        logging.debug(b1)
        b2 = Business(minutes=m, added_date='2021-09-04', business='new test business')
        b2.save()
        bu = BusinessUpdate(business=b1, update_date='2021-09-04', update_text="test update")
        bu.save()

        d = {'meeting_date': '2021-09-04', 'memberships': 5}
        response = self.client.post(reverse('minutes:minutes_form', kwargs={'minutes_id': m.id}), d, secure=True)
        self.assertEqual(Minutes.objects.last().memberships, 5)
        self.assertNotEqual(Minutes.objects.last().start_time, '19:30')
