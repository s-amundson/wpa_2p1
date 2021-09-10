import logging

from django.test import TestCase, Client
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from student_app.models import Student, User
from ..models import Level, Member
from ..src import RunDaily
logger = logging.getLogger(__name__)


class TestsRunDaily(TestCase):
    fixtures = ['f1', 'level']

    def test_expired_member(self):
        d_now = timezone.localtime(timezone.now()).date()
        student = Student.objects.get(pk=2)
        student.user.is_member = True
        student.user.save()
        member = Member(student=student, expire_date=d_now - timedelta(days=6), level=Level.objects.get(pk=1),
                        join_date=d_now - timedelta(days=600))
        member.save()
        RunDaily().expire()
        s = Student.objects.get(pk=2)
        self.assertFalse(s.user.is_member)

    def test_current_member(self):
        d_now = timezone.localtime(timezone.now()).date()
        student = Student.objects.get(pk=2)
        student.user.is_member = True
        student.user.save()
        member = Member(student=student, expire_date=d_now + timedelta(days=30), level=Level.objects.get(pk=1),
                        join_date=d_now - timedelta(days=600))
        member.save()
        RunDaily().expire()
        s = Student.objects.get(pk=2)
        self.assertTrue(s.user.is_member)

    def test_notice(self):
        d_now = timezone.localtime(timezone.now()).date()
        student = Student.objects.get(pk=2)
        student.user.is_member = True
        student.user.save()
        logging.debug(student.user.is_member)
        logging.debug(d_now)
        member = Member(student=student, expire_date=d_now + timedelta(days=14), level=Level.objects.get(pk=1),
                        join_date=d_now - timedelta(days=600))
        member.save()
        logging.debug(member.expire_date)
        RunDaily().expire()
        s = Student.objects.get(pk=2)
        self.assertTrue(s.user.is_member)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Membership Expiring')
