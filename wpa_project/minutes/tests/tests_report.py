import logging
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import Minutes, Business, BusinessUpdate, Report

logger = logging.getLogger(__name__)


class TestsReport(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    def test_get_report(self):
        response = self.client.get(reverse('minutes:report'), secure=True)
        self.assertTemplateUsed('minutes/forms/business_report_form.html')

    def test_get_report_existing(self):
        m = Minutes(
            meeting_date='2021-09-04', start_time='19:30', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()
        r = Report(report='Test Report', minutes=m, owner='president')
        r.save()

        response = self.client.get(reverse('minutes:report', kwargs={'report_id': r.id}), secure=True)
        self.assertTemplateUsed('minutes/forms/business_report_form.html')

    def test_post_report(self):
        m = Minutes(
            meeting_date='2021-09-04', start_time='19:30', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()

        d = {'report': 'test report', 'minutes': m.id, 'owner': 'president'}
        response = self.client.post(reverse('minutes:report'), d, secure=True)
        self.assertEqual(len(Report.objects.all()), 1)
        self.assertEqual(Report.objects.last().report, 'test report')

    def test_post_report_existing(self):
        m = Minutes(
            meeting_date='2021-09-04', start_time='19:30', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()
        r = Report(report='old Test Report', minutes=m, owner='president')
        r.save()

        d = {'report': 'test report', 'minutes': m.id, 'owner': 'president'}
        response = self.client.post(reverse('minutes:report', kwargs={'report_id': r.id}), d, secure=True)
        self.assertEqual(len(Report.objects.all()), 1)
        self.assertEqual(Report.objects.last().report, 'test report')
