import datetime
import logging
import json
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import JoadEvent, EventRegistration
from student_app.models.student import Student
logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadEventRegistration(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    # def test_user_normal_no_auth(self):
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.get(reverse('joad:event_registration'), secure=True)
    #     self.assertTemplateUsed(response, 'joad/event_registration.html')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.context['form'].fields), 1)
    #
    # def test_board_user_get(self):
    #     self.test_user = User.objects.get(pk=1)
    #     self.client.force_login(self.test_user)
    #     # allow user to access
    #     response = self.client.get(reverse('joad:event_registration'), secure=True)
    #     self.assertTemplateUsed(response, 'joad/event_registration.html')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.context['form'].fields), 5)

    # def test_student_get(self):
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.get(reverse('joad:event_registration'), secure=True)
    #     self.assertTemplateUsed(response, 'joad/event_registration.html')
    #     self.assertEqual(response.status_code, 200)

    # def test_student_post(self):
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 1}),
    #                                 {'event': 1, 'student_5': 'on'}, secure=True)
    #     # self.assertEqual(response.status_code, 200)
    #     events = EventRegistration.objects.all()
    #     self.assertEqual(len(events), 2)
    #     self.assertEqual(self.client.session['line_items'][0]['name'],
    #                      'Joad event on 2022-02-16 student id: 5')
    #     self.assertEqual(self.client.session['payment_db'][1], 'EventRegistration')
    #
    # def test_student_post_old(self):
    #     s = Student.objects.get(pk=5)
    #     s.dob = s.dob + datetime.timedelta(days=365 * 10)
    #     logging.debug(s.dob)
    #     s.save()
    #
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 1}),
    #                                 {'event': 1, 'student_5': 'on'}, secure=True)
    #     # self.assertEqual(response.status_code, 200)
    #     events = EventRegistration.objects.all()
    #     self.assertEqual(len(events), 1)
    #     self.assertContains(response, 'Student is to old.')
    #
    # def test_student_post_young(self):
    #     s = Student.objects.get(pk=5)
    #     s.dob = timezone.now() - datetime.timedelta(days=365 * 5)
    #     logging.debug(s.dob)
    #     s.save()
    #
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 1}),
    #                                 {'event': 1, 'student_5': 'on'}, secure=True)
    #     # self.assertEqual(response.status_code, 200)
    #     events = EventRegistration.objects.all()
    #     self.assertEqual(len(events), 1)
    #     self.assertContains(response, 'Student is to young.')

    # def test_student_post_reregister(self):
    #     s = Student.objects.get(pk=5)
    #     s.dob = timezone.now() - datetime.timedelta(days=365 * 10)
    #     logging.debug(s.dob)
    #     s.save()
    #     EventRegistration.objects.create(event=JoadEvent.objects.get(pk=1),
    #                                      student=Student.objects.get(pk=5),
    #                                      pay_status='paid',
    #                                      idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 1}),
    #                                 {'event': 1, 'student_5': 'on'}, secure=True)
    #     # self.assertEqual(response.status_code, 200)
    #     events = EventRegistration.objects.all()
    #     self.assertEqual(len(events), 2)
    #     self.assertContains(response, 'Student is already enrolled')
    #
    # def test_student_post_invalid(self):
    #     s = Student.objects.get(pk=5)
    #     s.dob = timezone.now() - datetime.timedelta(days=365 * 10)
    #     logging.debug(s.dob)
    #     s.save()
    #     EventRegistration.objects.create(event=JoadEvent.objects.get(pk=1),
    #                                      student=Student.objects.get(pk=5),
    #                                      pay_status='paid',
    #                                      idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
    #     self.test_user = User.objects.get(pk=3)
    #     self.client.force_login(self.test_user)
    #
    #     response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 1}),
    #                                 {'event': 1}, secure=True)
    #     # self.assertEqual(response.status_code, 200)
    #     events = EventRegistration.objects.all()
    #     self.assertEqual(len(events), 2)
    #     self.assertContains(response, 'Invalid student selected')

    def test_student_post_full(self):
        s = Student.objects.get(pk=5)
        s.dob = timezone.now() - datetime.timedelta(days=365 * 10)
        logging.debug(s.dob)
        s.save()
        j = JoadEvent.objects.get(pk=1)
        j.student_limit = 1
        j.save()
        # EventRegistration.objects.create(event=JoadEvent.objects.get(pk=1),
        #                                  student=Student.objects.get(pk=5),
        #                                  pay_status='paid',
        #                                  idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

        response = self.client.post(reverse('joad:event_registration', kwargs={"event_id": 1}),
                                    {'event': 1, 'student_5': 'on'}, secure=True)
        # self.assertEqual(response.status_code, 200)
        events = EventRegistration.objects.all()
        self.assertEqual(len(events), 1)
        self.assertContains(response, 'Class is full')
