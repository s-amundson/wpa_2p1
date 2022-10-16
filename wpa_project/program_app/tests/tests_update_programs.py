import logging
import uuid
from django.core import mail
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
        self.beginner_class_count = [16, 17, 18]

    def test_close_class(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc = BeginnerClass(class_date=d, class_type='combined', beginner_limit=10, returnee_limit=10, state='open')
        bc.save()

        UpdatePrograms().close_class(timezone.datetime.time(d))
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).state, 'closed')

    def test_beginner_class_recorded(self):
        d = timezone.localtime(timezone.now()).date() - timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc = BeginnerClass(class_date=d, class_type='combined', beginner_limit=10, returnee_limit=10, state='open')
        bc.save()

        UpdatePrograms().daily_update()
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).state, 'recorded')

    def test_email_staff_notice(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=3)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
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

        UpdatePrograms().status_email()
        self.assertEqual(mail.outbox[0].subject, f"WPA Class Status {d.strftime('%Y-%m-%d')}")
        s = 'has 2 students signed up and 3 volunteers signed up. The following volunteers are signed up:'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)

    def test_email_staff_notice_no_class(self):
        # set up the class on a different day.
        d = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
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

        UpdatePrograms().status_email()
        self.assertEqual(len(mail.outbox), 0)

    def test_email_beginner_reminder(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=18)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc1 = BeginnerClass(class_date=d, class_type='beginner', beginner_limit=3, beginner_wait_limit=5,
                            returnee_limit=0, state='open')
        bc1.save()
        u = User.objects.get(pk=3)
        u.is_staff = True
        u.is_instructor = True
        u.save()
        ps = ['paid', 'paid', 'paid', 'waiting', 'waiting']
        for i in range(5):
            cr = ClassRegistration(beginner_class=bc1,
                                   student=Student.objects.get(pk=i + 1),
                                   new_student=True,
                                   pay_status=ps[i],
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()

        # UpdatePrograms().beginner_class()
        UpdatePrograms().reminder_email(timezone.datetime.time(d))
        logging.warning(len(mail.outbox))
        for m in mail.outbox:
            logging.warning(m.subject)
        self.assertEqual(mail.outbox[0].subject, f"WPA Class Reminder {d.strftime('%Y-%m-%d')}")
        s = 'Either you or a member of your family is signed up for a class'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)
        self.assertTrue(mail.outbox[0].body.find('will not be allowed to participate') > 0)

        self.assertEqual(mail.outbox[1].subject, f"WPA Class Wait List Reminder {d.strftime('%Y-%m-%d')}")
        s = 'Either you or a member of your family is on the wait-list for a class'
        self.assertTrue(mail.outbox[1].body.find(s) > 0)
        self.assertTrue(mail.outbox[1].body.find('will not be allowed to participate') > 0)

    def test_email_returnee_reminder(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=11)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc1 = BeginnerClass(class_date=d, class_type='returnee', beginner_limit=0, returnee_limit=3,
                            returnee_wait_limit=5, state='open')
        bc1.save()
        u = User.objects.get(pk=3)
        u.is_staff = True
        u.is_instructor = True
        u.save()
        ps = ['paid', 'paid', 'paid', 'waiting', 'waiting']
        for i in range(5):
            cr = ClassRegistration(beginner_class=bc1,
                                   student=Student.objects.get(pk=i + 1),
                                   new_student=True,
                                   pay_status=ps[i],
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()

        UpdatePrograms().reminder_email(timezone.datetime.time(d))
        self.assertEqual(mail.outbox[0].subject, f"WPA Class Reminder {d.strftime('%Y-%m-%d')}")
        s = 'Either you or a member of your family is signed up for a class'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)
        self.assertEqual(mail.outbox[1].subject, f"WPA Class Wait List Reminder {d.strftime('%Y-%m-%d')}")
        s = 'Either you or a member of your family is on the wait-list for a class'
        self.assertTrue(mail.outbox[1].body.find(s) > 0)


class TestsUpdatePrograms2(TestCase):
    fixtures = ['beginner_schedule']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_add_class(self):
        UpdatePrograms().add_weekly()
        self.assertTrue(BeginnerClass.objects.all().count() in [18])
