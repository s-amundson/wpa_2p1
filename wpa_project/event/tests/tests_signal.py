import logging
import uuid

from django.test import TestCase, Client
from django.apps import apps
from django.utils import timezone

from ..models import Event, Registration
from payment.signals import payment_error_signal
from payment.models import PaymentLog
from student_app.models import Student
logger = logging.getLogger(__name__)


class TestsSignal(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_event_registration_signal_good_new(self):
        logger.warning('here')
        uid = '7b16fadf-4851-4206-8dc6-81a92b70e52f'
        event = Registration.objects.create(event=Event.objects.get(pk=1),
                                            student=Student.objects.get(pk=5),
                                            pay_status='started',
                                            idempotency_key=uid)

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

        er = Registration.objects.all()
        self.assertEqual(len(er), 1)
        er = Registration.objects.get(pk=event.id)
        self.assertEqual(er.pay_status, "paid")

    def test_signal_different_uuid(self):
        uid = uuid.uuid4()
        cr = Registration.objects.create(
            event=Event.objects.get(pk=1),
            student=Student.objects.get(pk=2),
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

        cr = Registration.objects.all()
        self.assertEqual(len(cr), 1)
        self.assertEqual(cr[0].pay_status, "started")

    def test_payment_error_signal_good(self):
        uid = uuid.uuid4()
        student = Student.objects.get(pk=2)
        cr = Registration.objects.create(
            event=Event.objects.get(pk=1),
            student=student,
            pay_status='started',
            idempotency_key=uid,
            user=student.user
        )
        cr.save()
        new_ik = uuid.uuid4()
        payment_error_signal.send(self.__class__, old_idempotency_key=uid, new_idempotency_key=new_ik)

        cr = Registration.objects.last()
        self.assertEqual(cr.idempotency_key, new_ik)