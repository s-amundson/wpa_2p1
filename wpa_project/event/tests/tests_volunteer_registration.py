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
        self.post_dict = {}

    def get_post_dict(self, event):
        self.post_dict = {
            'event': event.id,
            'registration_set-TOTAL_FORMS': 2,
            'registration_set-INITIAL_FORMS': 0,
            'registration_set-MIN_NUM_FORMS': 0,
            'registration_set-MAX_NUM_FORMS': 1000,
            'registration_set-0-register': True,
            'registration_set-0-student': 4,
            'registration_set-0-heavy': True,
            'registration_set-0-event': event.id,
            'registration_set-1-register': False,
            'registration_set-1-student': 5,
            'registration_set-1-heavy': False,
            'registration_set-1-event': event.id,
            }
        return self.post_dict

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
            reverse('events:registration'), self.get_post_dict(event),
            secure=True)

        self.assertRedirects(response, reverse('registration:profile'))
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)

    def tests_registration_post_good_id(self):
        d = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=4)
        event = Event.objects.get(pk=3)
        event.event_date = d
        event.save()

        response = self.client.post(
            reverse('events:registration', kwargs={'event': event.id}), self.get_post_dict(event),
            secure=True)

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
            self.get_post_dict(event),
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
        self.get_post_dict(event)
        self.post_dict['registration_set-0-student'] = 1
        response = self.client.post(
            reverse('events:registration', kwargs={'event': 3}),
            self.post_dict,
            secure=True)
        self.assertEqual(response.status_code, 200)
        cr = Registration.objects.all()
        self.assertEqual(len(cr), 0)
        self.assertContains(response, 'Error with form')
