import logging
import uuid
import time
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase, Client

from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student, User
from ..src import UpdatePrograms
logger = logging.getLogger(__name__)


class TestsUpdatePrograms(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()


    def test_beginner_class(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        bc = BeginnerClass(class_date=d, class_type='combined', beginner_limit=10, returnee_limit=10, state='open')
        bc.save()

        UpdatePrograms().beginner_class()
        # count is 11 on Saturdays
        self.assertTrue(BeginnerClass.objects.all().count() == 9 or BeginnerClass.objects.all().count() == 11)
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).state, 'closed')
        for i in range(8):
            self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 1 + i).state, 'open')
        # self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 2).state, 'open')

    def test_beginner_class_recorded(self):
        d = timezone.localtime(timezone.now()).date() - timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        bc = BeginnerClass(class_date=d, class_type='combined', beginner_limit=10, returnee_limit=10, state='open')
        bc.save()

        UpdatePrograms().beginner_class()
        # count is 11 on Saturdays
        self.assertTrue(BeginnerClass.objects.all().count() == 9 or BeginnerClass.objects.all().count() == 11)
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).state, 'recorded')
        for i in range(8):
            # self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 1 + i).state, 'open')
            self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 1 + i).state, 'open')
        # self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 2).state, 'open')

    def test_email_notice(self):
        d = timezone.localtime(timezone.now()).date() - timedelta(days=3)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        bc1 = BeginnerClass(class_date=d, class_type='beginner', beginner_limit=10, returnee_limit=0, state='open')
        bc1.save()
        bc2 = BeginnerClass(class_date=timezone.datetime(year=d.year, month=d.month, day=d.day, hour=11),
                            class_type='returnee', beginner_limit=0, returnee_limit=10, state='open')
        bc2.save()
        u = User.objects.get(pk=3)
        u.is_staff = True
        u.is_instructor = True
        u.save()

        for i in range(5):
            cr = ClassRegistration(beginner_class=bc1,
                                   student=Student.objects.get(pk=i + 1),
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()

        UpdatePrograms().beginner_class()
        # logging.debug(mail.outbox[0].message())
        logging.debug(d.strftime('%Y-%m-%d'))
        self.assertEqual(mail.outbox[0].subject, f"WPA Class Status {d.strftime('%Y-%m-%d')}")
        s = 'has 2 students signed up and 3 volunteers signed up. The following volunteers are signed up:'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)

    def test_email_notice_no_class(self):
        # set up the class on a different day.
        d = timezone.localtime(timezone.now()).date() - timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        bc1 = BeginnerClass(class_date=d, class_type='beginner', beginner_limit=10, returnee_limit=0, state='open')
        bc1.save()
        bc2 = BeginnerClass(class_date=timezone.datetime(year=d.year, month=d.month, day=d.day, hour=11),
                            class_type='returnee', beginner_limit=0, returnee_limit=10, state='open')
        bc2.save()
        u = User.objects.get(pk=3)
        u.is_staff = True
        u.is_instructor = True
        u.save()

        for i in range(5):
            cr = ClassRegistration(beginner_class=bc1,
                                   student=Student.objects.get(pk=i + 1),
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()

        UpdatePrograms().beginner_class()
        self.assertEqual(len(mail.outbox), 0)
