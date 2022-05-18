import logging
from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from student_app.models import Student
from ..models import JoadEvent, EventRegistration, PinAttendance

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsJoadIndex(TestCase):
    fixtures = ['f1', 'joad1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def set_event_date(self, date=None):
        if date is None:
            date = timezone.now() + timezone.timedelta(days=8)
        event = JoadEvent.objects.get(pk=1)
        event.event_date = date
        event.save()

    def test_user_normal_no_student(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.set_event_date()

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], False)
        self.assertEqual(len(response.context['students']), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['event_list']), 1)

    def test_staff_user_no_student(self):
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # allow user to access
        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], True)
        self.assertEqual(len(response.context['students']), 0)
        self.assertEqual(response.status_code, 200)

    def test_user_normal_not_joad(self):
        student = Student.objects.get(pk=5)
        student.dob = "1982-11-28"
        student.save()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        self.set_event_date()

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], False)
        self.assertEqual(len(response.context['students']), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['event_list']), 1)

    def test_user_normal_not_joad2(self):
        student = Student.objects.get(pk=10)
        student.is_joad = False
        student.save()
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        self.set_event_date()

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], True)
        self.assertEqual(len(response.context['students']), 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['event_list']), 1)
        registrations = response.context['session_list'][0]['registrations']
        logging.debug(registrations)
        self.assertTrue(registrations[0]['is_joad'])
        self.assertFalse(registrations[1]['is_joad'])
        self.assertTrue(registrations[2]['is_joad'])
        self.assertEqual(registrations[0]['reg_status'], 'not registered')
        self.assertEqual(registrations[1]['reg_status'], 'not registered')
        self.assertEqual(registrations[2]['reg_status'], 'not registered')
        logging.debug(registrations)

    def test_user_normal_is_joad(self):
        student = Student.objects.get(pk=5)
        student.dob = "1982-11-28"
        student.save()
        self.test_user = User.objects.get(pk=6)
        self.client.force_login(self.test_user)
        self.set_event_date()

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], True)
        self.assertEqual(len(response.context['students']), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['event_list']), 1)

    def test_user_normal_is_joad_registered(self):
        self.test_user = User.objects.get(pk=7)
        self.client.force_login(self.test_user)
        self.set_event_date()

        EventRegistration.objects.create(event=JoadEvent.objects.get(pk=1),
                                         student=Student.objects.get(pk=11),
                                         pay_status='paid',
                                         idempotency_key='7b16fadf-4851-4206-8dc6-81a92b70e52f')
        pa = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=11),
                                          attended=True)

        response = self.client.get(reverse('joad:index'), secure=True)
        self.assertEqual(response.context['is_auth'], True)
        self.assertEqual(len(response.context['students']), 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['event_list']), 1)
        logging.debug(response.context['event_list'][0])
        event = response.context['event_list'][0]
        self.assertEqual(len(event['registrations']), 3)
        self.assertEqual(event['registrations'][0]['reg_status'], 'not registered')
        self.assertEqual(event['registrations'][1]['reg_status'], 'registered')
        self.assertEqual(event['registrations'][2]['reg_status'], 'attending')
