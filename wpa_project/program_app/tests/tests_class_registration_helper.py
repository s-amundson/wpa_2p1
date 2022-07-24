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


class TestsClassRegistrationHelper(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crh = ClassRegistrationHelper()

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

    def test_update_status_beginner_full(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 3
        bc.returnee_limit = 0
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'full')

    def test_update_status_beginner_full_then_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 3
        bc.returnee_limit = 0
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'full')

        #  remove student
        cr = ClassRegistration.objects.last()
        cr.pay_status = 'refund'
        cr.save()

        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')

    def test_update_status_beginner_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 5
        bc.returnee_limit = 0
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')

    def test_update_status_returnee_full(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 3
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'full')

    def test_update_status_returnee_full_then_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 3
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'full')

        #  remove student
        cr = ClassRegistration.objects.last()
        cr.pay_status = 'refund'
        cr.save()

        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')

    def test_update_status_returnee_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 5
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')

    def test_update_status_returnee_full(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 3
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'full')