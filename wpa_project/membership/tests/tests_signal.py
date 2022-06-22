import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps
from django.utils import timezone
from datetime import date, timedelta

from ..models import Member, Membership, Level
from payment.models import PaymentLog
from student_app.models import Student, StudentFamily
logger = logging.getLogger(__name__)


class TestsSignal(TestCase):
    fixtures = ['f1', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_membership_signal_good_new(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:membership'), secure=True)
        self.assertEqual(response.status_code, 200)
        sf = Student.objects.get(user=self.test_user).student_family
        uid = uuid.uuid4()
        membership = Membership.objects.create(
            level=Level.objects.get(pk=1),
            pay_status='started',
            idempotency_key=uid
        )
        membership.students.set(sf.student_set.all())
        membership.save()

        log = PaymentLog.objects.create(user=self.test_user,
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

        members = Member.objects.all()
        self.assertEqual(len(members), 2)

    def test_membership_signal_different_uuid(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:membership'), secure=True)
        self.assertEqual(response.status_code, 200)
        sf = Student.objects.get(user=self.test_user).student_family
        uid = uuid.uuid4()
        membership = Membership.objects.create(
            level=Level.objects.get(pk=1),
            pay_status='started',
            idempotency_key=uid
        )
        membership.students.set(sf.student_set.all())
        membership.save()

        log = PaymentLog.objects.create(user=self.test_user,
                                        checkout_created_time=timezone.now(),
                                        description="square_response",
                                        location_id='location_id',
                                        idempotency_key=uuid.uuid4(),
                                        order_id='order_id',
                                        payment_id='id',
                                        receipt='receipt_url',
                                        source_type='source_type',
                                        status='SUCCESS',
                                        total_money=500,
                                        )
        log.save()

        members = Member.objects.all()
        self.assertEqual(len(members), 0)

    def test_membership_signal_good_renew(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:membership'), secure=True)
        self.assertEqual(response.status_code, 200)
        sf = Student.objects.get(user=self.test_user).student_family
        uid = uuid.uuid4()
        logging.debug(date.today() + timedelta(days=30))
        Member.objects.create(
            student=Student.objects.get(pk=2),
            expire_date=(date.today() + timedelta(days=30)).isoformat(),
            level=Level.objects.get(pk=1)
        ).save()
        Member.objects.create(
            student=Student.objects.get(pk=3),
            expire_date=date.today() + timedelta(days=30),
            level=Level.objects.get(pk=1)
        ).save()
        membership = Membership.objects.create(
            level=Level.objects.get(pk=1),
            pay_status='started',
            idempotency_key=uid
        )
        membership.students.set(sf.student_set.all())
        membership.save()

        log = PaymentLog.objects.create(user=self.test_user,
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

        members = Member.objects.all()
        self.assertEqual(len(members), 2)
        self.assertTrue(members[0].expire_date > date.today() + timedelta(days=380))

    def test_membership_signal_bad_new(self):
        # Get the page, if not super or board, page is forbidden
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('membership:membership'), secure=True)
        self.assertEqual(response.status_code, 200)
        sf = Student.objects.get(user=self.test_user).student_family
        uid = uuid.uuid4()
        membership = Membership.objects.create(
            level=Level.objects.get(pk=1),
            pay_status='started',
            idempotency_key=uid
        )
        membership.students.set(sf.student_set.all())
        membership.save()

        log = PaymentLog.objects.create(user=self.test_user,
                                        checkout_created_time=timezone.now(),
                                        description="square_response",
                                        location_id='location_id',
                                        idempotency_key=uid,
                                        order_id='order_id',
                                        payment_id='id',
                                        receipt='receipt_url',
                                        source_type='source_type',
                                        status='ERROR',
                                        total_money=500,
                                        )
        log.save()

        members = Member.objects.all()
        self.assertEqual(len(members), 0)
