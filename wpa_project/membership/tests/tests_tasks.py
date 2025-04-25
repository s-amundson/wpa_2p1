import logging

from django.test import TestCase, tag
from django.core import mail
from django.utils import timezone
from datetime import timedelta
import uuid

from student_app.models import Student, User
from payment.models import PaymentLog
from ..models import Level, Member, Membership
from ..tasks import membership_expire_notice, membership_expire_update, membership_user_update
logger = logging.getLogger(__name__)


class TestsTasks(TestCase):
    fixtures = ['f1', 'level']

    # @tag('temp')
    def test_expired_member(self):
        d_now = timezone.localtime(timezone.now()).date()
        student = Student.objects.get(pk=2)
        student.user.is_member = True
        student.user.save()
        member = Member(student=student, expire_date=d_now - timedelta(days=6), level=Level.objects.get(pk=1),
                        join_date=d_now - timedelta(days=600))
        member.save()
        membership_expire_update()
        s = Student.objects.get(pk=2)
        self.assertFalse(s.user.is_member)

    # @tag('temp')
    def test_current_member(self):
        d_now = timezone.localtime(timezone.now()).date()
        student = Student.objects.get(pk=2)
        student.user.is_member = True
        student.user.save()
        member = Member(student=student, expire_date=d_now + timedelta(days=30), level=Level.objects.get(pk=1),
                        join_date=d_now - timedelta(days=600))
        member.save()
        membership_expire_update()
        s = Student.objects.get(pk=2)
        self.assertTrue(s.user.is_member)

    # @tag('temp')
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
        membership_expire_notice()
        s = Student.objects.get(pk=2)
        self.assertTrue(s.user.is_member)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Woodley Park Archers Membership Expiring')

    # @tag('temp')
    def test_membership_user_update(self):
        # Get the page, if not super or board, page is forbidden

        sf = Student.objects.get(pk=2).student_family
        uid = uuid.uuid4()
        # make the payment log first so the signal doesn't work.
        log = PaymentLog.objects.create(user=User.objects.get(pk=2),
                                        checkout_created_time=timezone.now(),
                                        description="square_response",
                                        location_id='location_id',
                                        idempotency_key=uid,
                                        order_id='order_id',
                                        payment_id='id',
                                        receipt='receipt_url',
                                        source_type='source_type',
                                        status='SUCCESS',
                                        total_money=500,
                                        )
        log.save()
        membership = Membership.objects.create(
            level=Level.objects.get(pk=1),
            pay_status='start',
            idempotency_key=uid
        )
        membership.students.set(sf.student_set.all())
        membership.save()
        self.assertFalse(User.objects.get(pk=2).is_member)
        membership_user_update()
        members = Member.objects.all()
        # self.assertEqual(len(members), 2)
        self.assertTrue(User.objects.get(pk=2).is_member)