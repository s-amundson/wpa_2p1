import logging
import uuid
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from django.test import TestCase, Client, tag
from django.contrib.auth.models import Group
from unittest.mock import patch

from ..models import BeginnerClass, BeginnerSchedule
from event.models import Event, Registration, RegistrationAdmin
from .helper import create_beginner_class
from student_app.models import Student, User
from ..src import UpdatePrograms, EmailMessage
logger = logging.getLogger(__name__)

# @tag('temp')
class TestsUpdatePrograms(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.beginner_class_count = [16, 17, 18]
        self.staff_group = Group.objects.get(name='staff')
        self.instructor_group = Group.objects.get(name='instructors')
        self.test_user = User.objects.get(pk=3)
        self.test_user.groups.add(self.staff_group, self.instructor_group)

    def test_close_class(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc = create_beginner_class(d, 'open', 'combined', 10, 0)

        UpdatePrograms().close_class(timezone.datetime.time(d))
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).event.state, 'closed')

    def test_beginner_class_recorded(self):
        d = timezone.localtime(timezone.now()).date() - timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc = create_beginner_class(d, 'open', 'combined', 10, 0)

        UpdatePrograms().daily_update()
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).event.state, 'recorded')

    # @tag('temp')
    def test_email_staff_notice(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc1 = create_beginner_class(d, 'open', 'beginner')
        bc2 = create_beginner_class(timezone.datetime(year=d.year, month=d.month, day=d.day, hour=11), 'open', 'returnee')
        self.test_user.groups.remove(self.instructor_group)

        for i in range(5):
            cr = Registration(
                event=bc1.event,
                student=Student.objects.get(pk=i + 1),
                pay_status='paid',
                idempotency_key=str(uuid.uuid4()))
            cr.save()

        UpdatePrograms().status_email()
        self.assertEqual(mail.outbox[0].subject, f"WPA Class Status {d.strftime('%Y-%m-%d')}")
        # logger.warning(mail.outbox[0].body)
        s = 'has 2 students, 2 instructors, and 1 volunteers signed up. The following volunteers are signed up:'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)

    # @tag('temp')
    def test_email_staff_notice_instructor_canceled(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc1 = create_beginner_class(d, 'open', 'beginner')

        for i in range(5):
            cr = Registration(
                event=bc1.event,
                student=Student.objects.get(pk=i + 1),
                pay_status='paid',
                idempotency_key=str(uuid.uuid4()))
            cr.save()

        reg = Registration.objects.filter(event=bc1.event, student__user=self.test_user).last()
        reg.pay_status = 'canceled'
        reg.save()

        email_message = EmailMessage()
        email_message.instructor_canceled_email(bc1.event, 2)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Instructor Cancellation')
        # logger.warning(mail.outbox[0].body)
        s = "One of our instructors can't make it to the event"
        self.assertTrue(mail.outbox[0].body.find(s) > 0)
        s = 'and we now have 2 signed up.'
        self.assertTrue(mail.outbox[0].body.find(s) > 0)

    def test_email_staff_notice_no_class(self):
        # set up the class on a different day.
        d = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc1 = create_beginner_class(d, 'open', 'beginner', 10, 0)
        bc2 = create_beginner_class(timezone.datetime(year=d.year, month=d.month, day=d.day, hour=11), 'open',
                                    'returnee', 0, 10)


        for i in range(5):
            cr = Registration(
                event=bc1.event,
                student=Student.objects.get(pk=i + 1),
                pay_status='paid',
                idempotency_key=str(uuid.uuid4()))
            cr.save()

        UpdatePrograms().status_email()
        self.assertEqual(len(mail.outbox), 0)

    def test_email_beginner_reminder(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=18)
        d = timezone.make_aware(d, timezone.get_current_timezone())
        bc1 = create_beginner_class(d, 'open', 'beginner', 3, 0)
        bc1.beginner_wait_limit = 5
        bc1.save()

        ps = ['paid', 'paid', 'paid', 'waiting', 'waiting']
        for i in range(5):
            cr = Registration(
                event=bc1.event,
                student=Student.objects.get(pk=i + 1),
                pay_status=ps[i],
                idempotency_key=str(uuid.uuid4()))
            cr.save()

        # UpdatePrograms().beginner_class()
        UpdatePrograms().reminder_email(timezone.datetime.time(d))
        # logger.warning(mail.outbox[0].body)
        for m in mail.outbox:
            logger.warning(m.subject)
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
        bc1 = create_beginner_class(d, 'open', 'returnee', 0, 3)
        bc1.returnee_wait_limit = 5
        bc1.save()

        ps = ['paid', 'paid', 'paid', 'waiting', 'waiting']
        for i in range(5):
            cr = Registration(
                event=bc1.event,
                student=Student.objects.get(pk=i + 1),
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

    # @tag('temp')
    def test_hourly_update_close(self):
        now = timezone.localtime(timezone.now())
        BeginnerSchedule.objects.create(
            class_time=now - timedelta(minutes=15),
            day_of_week=(now + timedelta(days=1)).weekday(),
            state='open',
            beginner_limit=10,
            returnee_limit=10,
        )
        UpdatePrograms().hourly_update()
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc.count(), 8)

    # @tag('temp')
    @patch('program_app.src.update_program.UpdatePrograms.reminder_email')
    def test_hourly_update_reminder(self, reminder_email):
        logger.warning(BeginnerClass.objects.all().count())
        now = timezone.localtime(timezone.now())
        bs = BeginnerSchedule.objects.create(
            class_time=(now - timedelta(minutes=15)).time().replace(second=0, microsecond=0),
            day_of_week=(now + timedelta(days=2)).weekday(),
            state='open',
            beginner_limit=10,
            returnee_limit=10,
        )
        UpdatePrograms().hourly_update()
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc.count(), 2)
        reminder_email.assert_called_with(bs.class_time)


class TestsUpdatePrograms2(TestCase):
    fixtures = ['beginner_schedule']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_add_class(self):
        UpdatePrograms().add_weekly()
        self.assertEqual(BeginnerClass.objects.all().count(), 20)

    def test_create_class_1(self):
        sch = BeginnerSchedule.objects.get(pk=1)
        UpdatePrograms().create_class(sch)
        bc = BeginnerClass.objects.all()
        events = Event.objects.all()
        self.assertEqual(bc.count(), 6)
        self.assertEqual(events.count(), 6)
        self.assertEqual(bc[0].class_type, 'beginner')
        self.assertEqual(timezone.localtime(bc[0].event.event_date).time(), sch.class_time)

        # do it again and don't create classes
        UpdatePrograms().create_class(sch)
        bc = BeginnerClass.objects.all()
        events = Event.objects.all()
        self.assertEqual(bc.count(), 6)
        self.assertEqual(events.count(), 6)
        self.assertEqual(bc[0].class_type, 'beginner')
        self.assertEqual(timezone.localtime(bc[0].event.event_date).time(), sch.class_time)

    def test_create_class_2(self):
        sch = BeginnerSchedule.objects.get(pk=2)
        UpdatePrograms().create_class(sch)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc.count(), 6)
        self.assertEqual(bc[0].class_type, 'returnee')
        self.assertEqual(timezone.localtime(bc[0].event.event_date).time(), sch.class_time)

    def test_create_class_4(self):
        sch = BeginnerSchedule.objects.get(pk=4)
        UpdatePrograms().create_class(sch)
        bc = BeginnerClass.objects.all()
        self.assertEqual(bc.count(), 2)
        self.assertEqual(bc[0].class_type, 'special')
        self.assertEqual(timezone.localtime(bc[0].event.event_date).time(), sch.class_time)
