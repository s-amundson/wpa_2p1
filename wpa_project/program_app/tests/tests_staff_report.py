import logging

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from event.models import Registration

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsStaffReport(TestCase):
    fixtures = ['f1', 'f2']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.url = reverse('programs:staff_attendance')

    def test_get_sign_in_page_bad(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_sign_in_page_good(self):
        cr = Registration.objects.get(pk=1)
        cr.pay_status = 'paid'
        cr.save()

        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/staff_attend_report.html')
        self.assertEqual(len(response.context['staff_list']), 2)
        self.assertEqual(response.context['staff_list'][0]['registrations'], 0)
        self.assertEqual(response.context['staff_list'][0]['attended'], 0)
        self.assertEqual(response.context['staff_list'][1]['registrations'], 1)
        self.assertEqual(response.context['staff_list'][1]['attended'], 0)

    def test_post_sign_in_page_good(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, {'start_date': '2022-02-01', 'end_date': '2022-03-01'}, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/staff_attend_report.html')
        self.assertEqual(len(response.context['staff_list']), 2)
        self.assertEqual(response.context['staff_list'][0]['registrations'], 0)
        self.assertEqual(response.context['staff_list'][0]['attended'], 0)
        self.assertEqual(response.context['staff_list'][0]['registrations'], 0)
        self.assertEqual(response.context['staff_list'][0]['attended'], 0)

    def test_get_sign_in_page_good_inactive_staff(self):
        u = User.objects.get(pk=2)
        u.is_active = False
        u.save()

        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'program_app/staff_attend_report.html')
        self.assertEqual(len(response.context['staff_list']), 1)
        self.assertEqual(response.context['staff_list'][0]['registrations'], 0)
        self.assertEqual(response.context['staff_list'][0]['attended'], 0)

