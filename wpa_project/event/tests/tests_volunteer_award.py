import logging
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone

from ..models import Event, VolunteerAward, VolunteerRecord
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
    def test_award_form_get(self):
        response = self.client.get(reverse('events:volunteer_award'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/award_form.html')

    # @tag('temp')
    def test_award_list_get(self):
        response = self.client.get(reverse('events:volunteer_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/award_form.html')

    # @tag('temp')
    def tests_award_post_new(self):
        event = Event.objects.get(pk=4)
        event.event_date = timezone.now() - timezone.timedelta(days=10)
        event.save()

        vr = VolunteerRecord.objects.create(
            event=event,
            student=Student.objects.get(pk=2),
            volunteer_points=2
        )
        response = self.client.post(
            reverse('events:volunteer_award'),
            {'description': '', 'events': [4], 'award': 'a thanks', 'student': ['']},
            secure=True)
        awards = VolunteerAward.objects.all()
        self.assertEqual(len(awards), 1)
        self.assertRedirects(response, reverse('events:volunteer_award', kwargs={'pk': awards[0].id}))

    # @tag('temp')
    def tests_award_post_no_volunteer(self):
        event = Event.objects.get(pk=4)
        event.event_date = timezone.now() - timezone.timedelta(days=10)
        event.save()

        response = self.client.post(
            reverse('events:volunteer_award'),
            {'description': '', 'events': [4], 'award': 'a thanks', 'student': ['']},
            secure=True)
        awards = VolunteerAward.objects.all()
        self.assertEqual(len(awards), 0)
        self.assertContains(response, 'No eligible volunteers for this event')
