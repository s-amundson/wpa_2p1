import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import Event, Registration
from student_app.models import Student, User

logger = logging.getLogger(__name__)


class TestsVolunteerRegistration(TestCase):
    fixtures = ['f1', 'volunteer1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

    def test_registration_get(self):
        response = self.client.get(reverse('events:registration'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/registration.html')

    def test_registration_get_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('events:registration'), secure=True)
        self.assertEqual(response.status_code, 302)

    def test_registration_get_with_event(self):
        response = self.client.get(reverse('events:registration', kwargs={'event': 3}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/registration.html')

    def tests_registration_post_good(self):
        d = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=4)
        event = Event.objects.get(pk=3)
        event.event_date = d
        event.save()

        response = self.client.post(
            reverse('events:registration', kwargs={'event': 3}),
            {'event': '3', 'student_4': 'on', 'terms': 'on'},
            secure=True)
        # self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('registration:profile'))
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)

    def tests_registration_post_twice(self):
        d = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=4)
        event = Event.objects.get(pk=3)
        event.event_date = d
        event.save()

        student = Student.objects.get(pk=4)

        Registration.objects.create(
            event=event,
            idempotency_key=uuid.uuid4(),
            pay_status='paid',
            student=student,
            user=self.test_user
        )

        response = self.client.post(
            reverse('events:registration', kwargs={'event': 3}),
            {'event': '3', 'student_4': 'on', 'terms': 'on'},
            secure=True)
        self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, reverse('registration:profile'))
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertContains(response, 'Student is already enrolled')

    def tests_registration_post_invalid_student(self):
        d = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=4)
        event = Event.objects.get(pk=3)
        event.event_date = d
        event.save()

        response = self.client.post(
            reverse('events:registration', kwargs={'event': 3}),
            {'event': '3', 'student_1': 'on', 'terms': 'on'},
            secure=True)
        self.assertEqual(response.status_code, 200)
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 0)
        self.assertContains(response, 'Invalid student selected')