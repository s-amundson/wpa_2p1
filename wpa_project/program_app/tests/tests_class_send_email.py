import logging
import uuid

from django.apps import apps
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..tasks import instructor_canceled
from .helper import create_beginner_class

from event.models import Event, Registration
from student_app.models import Student

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsClassSendEmail(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.test_dict = {'message': 'Test message', 'subject': 'Test Subject'}

    def test_get_send_email_bad(self):
        response = self.client.get(reverse('programs:send_email'), secure=True)
        self.assertEqual(response.status_code, 403)

    def test_get_send_email_good(self):
        response = self.client.get(reverse('programs:send_email', kwargs={'beginner_class': 1}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/form_as_p.html')

    def test_post_send_email_good(self):
        cr = Registration(event=Event.objects.get(pk=1),
                          student=Student.objects.get(pk=4),
                          pay_status='paid',
                          idempotency_key=str(uuid.uuid4()))
        cr.save()
        response = self.client.post(reverse('programs:send_email', kwargs={'beginner_class': 1}), self.test_dict,
                                    secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertTrue(mail.outbox[0].body.find('Test message') >= 0)

    def test_instructor_canceled(self):
        bc = create_beginner_class(
            date=(timezone.now() + timezone.timedelta(days=5)).replace(hour=9, minute=0, second=0),
            state='open',
            class_type='beginner'
        )
        instructor_canceled(bc.event)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Instructor Cancellation')
