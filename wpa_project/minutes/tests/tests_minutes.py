import logging
import json
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.apps import apps
from unittest.mock import patch
from django.utils import timezone

# from src.mixin import StudentFamilyMixin
from student_app.models import Student
from membership.models import Member, Level
from ..models import Minutes, Business, BusinessUpdate, Report

logger = logging.getLogger(__name__)


class TestsMinutes(TestCase):
    fixtures = ['f1', 'level', 'member1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')


    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        d_now = timezone.localtime(timezone.now()).date()
        student = Student.objects.get(pk=1)
        student.user.is_member = True
        student.user.save()
        member = Member.objects.create(student=student, expire_date=d_now + timezone.timedelta(days=30),
                                       level=Level.objects.get(pk=1), join_date=d_now - timezone.timedelta(days=600))
        member.save()
        self.post_dict = {
            'meeting_date': '2021-09-04 19:30',
            'memberships': 0,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }

    # @tag('temp')
    def test_minutes_list(self):
        # Get the page, if not super or board, page is forbidden
        response = self.client.get(reverse('minutes:minutes_list'), secure=True)
        self.assertTemplateUsed('minutes/minutes_list.html')

    # @tag('temp')
    def test_get_minutes_new(self):
        response = self.client.get(reverse('minutes:minutes'), secure=True)
        self.assertIsNone(response.context['minutes'])
        self.assertTemplateUsed('minutes/minutes.html')

    # @tag('temp')
    def test_get_minutes_unauthorized(self):
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('minutes:minutes'), secure=True)
        self.assertEqual(response.status_code, 403)

    # @tag('temp')
    def test_get_minutes_old(self):
        m = Minutes(
            meeting_date='2021-09-04T19:20:30+03:00', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()
        logger.debug(m)

        r = Report(report='Test Report', minutes=m, owner='president')
        r.save()
        b1 = Business(minutes=None, added_date='2021-08-04T13:20:30+03:00', business='Some old test business')
        b1.save()
        logger.debug(b1.added_date)
        b2 = Business(minutes=m, added_date='2021-09-04T19:25:30+03:00', business='new test business')
        b2.save()
        bu = BusinessUpdate(business=b1, update_date='2021-09-04T19:30:30+03:00', update_text="test update")
        bu.save()

        response = self.client.get(reverse('minutes:minutes', kwargs={'minutes': m.id}), secure=True)

        self.assertEqual(response.context['minutes'].id, m.id)
        self.assertEqual(len(response.context['formset']), 2)
        self.assertEqual(len(response.context['old_businesses']), 1)
        self.assertEqual(len(response.context['new_business']), 1)

    # @tag('temp')
    # def test_post_minutes_unauthorized(self):
    #     self.test_user = self.User.objects.get(pk=2)
    #     self.client.force_login(self.test_user)
    #     response = self.client.post(reverse('minutes:minutes'), secure=True)
    #     self.assertEqual(response.status_code, 403)

    # @tag('temp')
    def test_post_minutes_from_new(self):
        response = self.client.post(reverse('minutes:minutes'), self.post_dict, secure=True)
        m = Minutes.objects.all()
        self.assertEqual(len(m), 1)

    # @tag('temp')
    def test_post_minutes_old(self):
        m = Minutes(
            meeting_date='2021-09-04 19:30', attending='', minutes_text='', memberships=0,
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

        self.post_dict['balance'] = 216.2
        self.post_dict['memberships'] = 5
        # d = {'meeting_date': '2021-09-04', 'memberships': 5, 'balance': }
        response = self.client.post(reverse('minutes:minutes', kwargs={'minutes': m.id}), self.post_dict, secure=True)
        mr = Minutes.objects.last()
        self.assertEqual(mr.memberships, 5)
        self.assertNotEqual(mr.meeting_date, '2021-09-04 19:30')
        self.assertEqual(mr.balance, 216.2)
