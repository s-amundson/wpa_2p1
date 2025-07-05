import logging
import json

from django.test import TestCase, Client, tag
from django.urls import reverse

from event.models import Event, Registration
from student_app.models import Student, User

logger = logging.getLogger(__name__)


# @tag('temp')
class TestsClassStatus(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

    def test_class_status(self):
        self.client.force_login(User.objects.get(pk=3))

        response = self.client.get(reverse('programs:class_status', kwargs={'class_id': '1'}), secure=True)
        content = json.loads(response.content)
        self.assertEqual(content['status'], 'open')
        self.assertEqual(content['beginner'], 2)
        self.assertEqual(content['returnee'], 2)

        # add 1 beginner students and 1 returnee.
        cr = Registration(
            event=Event.objects.get(pk=1),
            student=Student.objects.get(pk=4),
            pay_status="paid",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()
        cr = Registration(
            event=Event.objects.get(pk=1),
            student=Student.objects.get(pk=5),
            pay_status="paid",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()

        response = self.client.get(reverse('programs:class_status', kwargs={'class_id': '1'}), secure=True)
        content = json.loads(response.content)
        self.assertEqual(content['status'], 'open')
        self.assertEqual(content['beginner'], 1)
        self.assertEqual(content['returnee'], 1)

    def test_class_status_null(self):
        self.client.force_login(User.objects.get(pk=3))

        response = self.client.get(reverse('programs:class_status', kwargs={'class_id': 'null'}), secure=True)
        self.assertEqual(response.status_code, 400)
