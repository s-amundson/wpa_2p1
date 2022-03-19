import datetime
import logging
import json
import time
import uuid

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..src import ClassRegistrationHelper
from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student, StudentFamily, User

logger = logging.getLogger(__name__)


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
        cr = ClassRegistration(
            beginner_class=BeginnerClass.objects.get(pk=1),
            student=Student.objects.get(pk=4),
            new_student=True,
            pay_status="paid",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()
        cr = ClassRegistration(
            beginner_class=BeginnerClass.objects.get(pk=1),
            student=Student.objects.get(pk=5),
            new_student=False,
            pay_status="paid",
            idempotency_key="7b16fadf-4851-4206-8dc6-81a92b70e52f",
            reg_time='2021-06-09',
            attended=False)
        cr.save()

        response = self.client.get(reverse('programs:class_status', kwargs={'class_id': '1'}), secure=True)
        content = json.loads(response.content)
        logging.debug(content)
        self.assertEqual(content['status'], 'open')
        self.assertEqual(content['beginner'], 1)
        self.assertEqual(content['returnee'], 1)

    def test_class_status_null(self):
        self.client.force_login(User.objects.get(pk=3))

        response = self.client.get(reverse('programs:class_status', kwargs={'class_id': 'null'}), secure=True)
        self.assertEqual(response.status_code, 400)
