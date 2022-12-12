import logging
import time
import uuid
from django.test import TestCase, Client
from django.apps import apps
from django.utils import timezone

from event.models import Event, Registration
from payment.models import PaymentLog
from payment.signals import payment_error_signal
from student_app.models import Student, StudentFamily
User = apps.get_model('student_app', 'User')

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
                                        idempotency_key=uid,
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
        self.assertEqual(cr[0].pay_status, "paid")

    def test_membership_signal_different_uuid(self):
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

    # def test_off_wait_list_email(self):
    #     # set up beginner class to have wait list
    #     bc = BeginnerClass.objects.get(pk=1)
    #     bc.class_type = 'beginner'
    #     bc.beginner_limit = 2
    #     bc.beginner_wait_limit = 10
    #     bc.returnee_limit = 0
    #     bc.returnee_wait_limit = 0
    #     bc.save()
    #
    #     # add 2 more to the wait list at the same time so they go together.
    #     user = User.objects.get(pk=3)
    #     ik = str(uuid.uuid4())
    #     for i in range(2):
    #         s = Student.objects.get(pk=i + 5)
    #         s.safety_class = "2023-06-05"
    #         s.save()
    #         cr = ClassRegistration(beginner_class=bc,
    #                                student=s,
    #                                new_student=False,
    #                                pay_status='waiting',
    #                                idempotency_key=ik,
    #                                user=user)
    #         cr.save()
    #     registrations = ClassRegistration.objects.all()
    #     update_wait_list_signal.send(self.__class__, beginner_class=bc)
    #     # time.sleep(3)
    #     # EmailMessage().wait_list_off(registrations)
    #     self.assertEqual(len(mail.outbox), 1)