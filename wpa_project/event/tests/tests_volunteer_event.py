import logging
import uuid
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone

from ..models import Event, VolunteerRecord, Registration
from ..tasks import cancel_event
from student_app.models import User, Student

logger = logging.getLogger(__name__)


class TestsVolunteerEvent(TestCase):
    fixtures = ['f1', 'volunteer1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    # @tag('temp')
    def test_event_get(self):
        response = self.client.get(reverse('events:volunteer_event'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/event_update.html')

    # @tag('temp')
    def test_event_get_no_auth(self):
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('events:volunteer_event'), secure=True)
        self.assertEqual(response.status_code, 403)

    # @tag('temp')
    def test_event_get_id(self):
        response = self.client.get(reverse('events:volunteer_event', kwargs={'event': 3}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/event_update.html')

    # @tag('temp')
    def tests_event_post_new(self):
        d = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=2)
        response = self.client.post(
            reverse('events:volunteer_event'),
            {'volunteer_limit': 4, 'event_date': d, 'state': 'open', 'description':'Updated description',
             'volunteer_points': 10},
            secure=True)
        # self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('events:volunteer_event_list'))
        event = Event.objects.get(pk=5)
        ve = event.volunteerevent_set.last()
        logger.warning(ve.description)
        self.assertEqual(event.state, 'open')
        self.assertEqual(event.type, 'work')
        self.assertEqual(event.volunteer_points, 10)
        self.assertEqual(ve.description, 'Updated description')

    # @tag('temp')
    def tests_event_post_id(self):
        d = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=2)
        response = self.client.post(
            reverse('events:volunteer_event', kwargs={'event': 3}),
            {'volunteer_limit': 4, 'event': 3, 'event_date': d, 'state': 'open',
             'description':'Updated description', 'volunteer_points': 10},
            secure=True)
        # self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('events:volunteer_event_list'))
        event = Event.objects.get(pk=3)
        logging.warning(event.volunteerevent_set)
        ve = event.volunteerevent_set.last()
        logger.warning(ve.description)
        self.assertEqual(event.state, 'open')
        self.assertEqual(event.type, 'work')
        self.assertEqual(event.event_date, d)
        self.assertEqual(ve.description, 'Updated description')

    # @tag('temp')
    @patch('event.tasks.cancel_event.delay')
    def tests_event_post_cancel(self, cancel_event):
        event = Event.objects.get(pk=3)
        student = Student.objects.get(pk=4)
        Registration.objects.create(
            event=event,
            idempotency_key=uuid.uuid4(),
            pay_status='paid',
            student=student,
            user=User.objects.get(pk=3)
        )
        d = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=2)
        response = self.client.post(
            reverse('events:volunteer_event', kwargs={'event': 3}),
            {'volunteer_limit': 4, 'event': 3, 'event_date': d, 'state': 'canceled',
             'description': 'Updated description', 'cancel_message': 'testing reasons', 'volunteer_points': 10},
            secure=True)
        # self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('events:volunteer_event_list'))
        event = Event.objects.get(pk=3)
        logging.warning(event.volunteerevent_set)
        ve = event.volunteerevent_set.last()
        logger.warning(ve.description)
        self.assertEqual(event.state, 'canceled')
        self.assertEqual(event.type, 'work')
        cancel_event.assert_called_with(3, 'testing reasons')

    # @tag('temp')
    def test_volunteer_record_get(self):
        response = self.client.get(reverse('events:volunteer_record'), secure=True)
        self.assertEqual(response.status_code, 200)

    # @tag('temp')
    def test_volunteer_record_get_student(self):
        response = self.client.get(reverse('events:volunteer_record'), {'student': 3}, secure=True)
        self.assertEqual(response.status_code, 200)

    # @tag('temp')
    def test_volunteer_record_get_student_family(self):
        response = self.client.get(reverse('events:volunteer_record'), {'student_family': 3}, secure=True)
        self.assertEqual(response.status_code, 200)

    # @tag('temp')
    def test_volunteer_record_post(self):
        response = self.client.post(reverse('events:volunteer_record'),
                                   {'student': 2, 'volunteer_points': 2}, secure=True)
        vr = VolunteerRecord.objects.all()
        self.assertEqual(len(vr), 1)
        self.assertEqual(vr[0].volunteer_points, 2)

    # @tag('temp')
    def test_task_cancel_event(self):
        event = Event.objects.get(pk=3)
        event.event_date = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timezone.timedelta(days=2)
        event.save()
        student = Student.objects.get(pk=4)
        Registration.objects.create(
            event=event,
            idempotency_key=uuid.uuid4(),
            pay_status='paid',
            student=student,
            user=User.objects.get(pk=3)
        )

        cancel_event(3, 'testing reasons')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Cancellation')
        self.assertTrue(mail.outbox[0].body.find('testing reasons') >= 0)
        self.assertTrue(mail.outbox[0].body.find('The volunteer event') >= 0)
