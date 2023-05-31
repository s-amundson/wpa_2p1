import logging

from django.test import TestCase, Client
from django.apps import apps
from django.utils import timezone

from ..models import JoadEvent, Registration, PinAttendance, Session

from payment.models import PaymentLog
from student_app.models import Student
logger = logging.getLogger(__name__)


class TestsSignal(TestCase):
    fixtures = ['f1', 'joad1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)

    def test_registration_signal_good_new(self):
        uid = '7b16fadf-4851-4206-8dc6-81a92b70e52f'
        s = Student.objects.get(user=self.test_user)
        event = Registration.objects.create(session=Session.objects.get(pk=1),
                                            student=s,
                                            pay_status='started',
                                            idempotency_key=uid)

        log = PaymentLog.objects.create(user=self.test_user,
                                        # student_family=Student.objects.get(user=self.test_user).student_family,
                                        checkout_created_time=timezone.now(),
                                        # db_model='Registration',
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

    def test_pin_attendance_signal_good_new(self):
        uid = '7b16fadf-4851-4206-8dc6-81a92b70e52f'
        pinattendance = PinAttendance.objects.create(event=JoadEvent.objects.get(pk=1),
                                          student=Student.objects.get(pk=10),
                                          attended=True,
                                          pay_status='started',
                                          idempotency_key=uid)

        log = PaymentLog.objects.create(user=self.test_user,
                                        # student_family=Student.objects.get(user=self.test_user).student_family,
                                        checkout_created_time=timezone.now(),
                                        # db_model='PinAttendance',
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

        pa = PinAttendance.objects.all()
        self.assertEqual(len(pa), 1)
        pa = PinAttendance.objects.get(pk=pinattendance.id)
        self.assertEqual(pa.pay_status, "paid")
