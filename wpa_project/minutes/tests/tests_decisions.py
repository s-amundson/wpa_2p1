import logging
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.apps import apps

from ..models import Minutes, Decision, Report

logger = logging.getLogger(__name__)


class TestsDecision(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    # @tag('temp')
    def test_get_decision(self):
        response = self.client.get(reverse('minutes:decision'), secure=True)
        self.assertTemplateUsed('minutes/forms/decision_form.html')

    # @tag('temp')
    def test_get_decision_no_auth(self):
        self.test_user = self.User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('minutes:decision'), secure=True)
        self.assertEqual(response.status_code, 403)

    # @tag('temp')
    def test_get_report_existing(self):

        d = Decision(decision_date='2021-12-20', text='test decision')
        d.save()

        response = self.client.get(reverse('minutes:decision', kwargs={'decision_id': d.id}), secure=True)
        self.assertTemplateUsed('minutes/forms/decision_form.html')

    # @tag('temp')
    def test_post_report(self):
        m = Minutes(
            meeting_date='2021-09-04 19:30', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()

        d = {'text': 'test decision'}
        response = self.client.post(reverse('minutes:decision'), d, secure=True)
        self.assertEqual(len(Decision.objects.all()), 1)
        self.assertEqual(Decision.objects.last().text, 'test decision')

    # @tag('temp')
    def test_post_report_no_auth(self):
        self.test_user = self.User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        m = Minutes(
            meeting_date='2021-09-04 19:30', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()

        d = {'text': 'test decision'}
        response = self.client.post(reverse('minutes:decision'), d, secure=True)
        self.assertEqual(len(Decision.objects.all()), 0)

    # @tag('temp')
    def test_post_report_existing(self):
        r = Decision(decision_date='2021-12-20', text='old decision')
        r.save()

        d = {'decision_date': '2021-12-20', 'text': 'updated decision'}
        response = self.client.post(reverse('minutes:decision', kwargs={'decision_id': r.id}), d, secure=True)
        self.assertEqual(len(Decision.objects.all()), 1)
        self.assertEqual(Decision.objects.last().text, 'updated decision')

    # @tag('temp')
    def test_get_decision_list(self):
        r = Decision(decision_date='2021-12-20', text='old decision')
        r.save()

        response = self.client.get(reverse('minutes:decision_list'), secure=True)
        self.assertTemplateUsed('minutes/minutes_list.html')
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(len(Decision.objects.all()), 1)
