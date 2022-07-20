import logging
import uuid
from django.test import TestCase, Client
from django.apps import apps
from django.utils import timezone

from ..models import BeginnerClass, ClassRegistration
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

    def test_registration_signal_good_new(self):
        # sf = self.test_user.studentfamily_set.all()
        # sf = Student.objects.get(user=sef.user).student_family
        uid = uuid.uuid4()
        cr = ClassRegistration.objects.create(
            beginner_class=BeginnerClass.objects.get(pk=1),
            student=Student.objects.get(pk=2),
            new_student=True,
            pay_status='started',
            idempotency_key=uid
        )
        cr.save()

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

        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].pay_status, "paid")

    def test_membership_signal_different_uuid(self):
        uid = uuid.uuid4()
        cr = ClassRegistration.objects.create(
            beginner_class=BeginnerClass.objects.get(pk=1),
            student=Student.objects.get(pk=2),
            new_student=True,
            pay_status='started',
            idempotency_key=uid
        )
        cr.save()

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

        cr = ClassRegistration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].pay_status, "started")
