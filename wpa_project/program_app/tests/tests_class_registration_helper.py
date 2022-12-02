import logging
import uuid
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, Client

from ..src import ClassRegistrationHelper
from ..models import BeginnerClass, ClassRegistration
from ..tasks import update_waiting
from student_app.models import Student, User
from payment.tests import MockSideEffects

logger = logging.getLogger(__name__)


class TestsClassRegistrationHelper(MockSideEffects, TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crh = ClassRegistrationHelper()

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)

    def test_update_status_beginner_full(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 3
        bc.returnee_limit = 0
        bc.save()
        for i in range(5):
            s = Student.objects.get(pk=i + 1)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')

    def test_update_status_beginner_full_then_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 3
        bc.returnee_limit = 0
        bc.save()
        for i in range(5):
            s = Student.objects.get(pk=i + 1)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')

        #  remove student
        cr = ClassRegistration.objects.last()
        cr.pay_status = 'refund'
        cr.save()

        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')

    def test_update_status_beginner_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 5
        bc.returnee_limit = 0
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')

    def test_update_status_returnee_full(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 3
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')

    def test_update_status_returnee_full_then_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 3
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')

        #  remove student
        cr = ClassRegistration.objects.last()
        cr.pay_status = 'refund'
        cr.save()

        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')

    def test_update_status_returnee_open(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 5
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'open')

    @patch('program_app.src.class_registration_helper.PaymentHelper.create_payment')
    def test_update_status_beginner_waiting(self, mock_payment):
        mock_payment.side_effect = self.payment_side_effect
        # set up beginner class to have wait list
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 2
        bc.beginner_wait_limit = 10
        bc.returnee_limit = 0
        bc.save()

        # add 2 students paid and one waiting
        user = User.objects.get(pk=2)
        self.add_card(user)
        ps = ['paid', 'paid', 'waiting']
        for i in range(3):
            s = Student.objects.get(pk=i + 2)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status=ps[i],
                                   idempotency_key=str(uuid.uuid4()),
                                   user=user)
            cr.save()

        # add 2 more to the wait list at the same time so that they go together.
        user = User.objects.get(pk=3)
        self.add_card(user)
        ik = str(uuid.uuid4())
        for i in range(2):
            s = Student.objects.get(pk=i + 5)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='waiting',
                                   idempotency_key=ik,
                                   user=user)
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'wait')
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 3)

        # change wait  limit to 2 so that the class is full.
        bc.beginner_wait_limit = 2
        bc.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')


        # chang the beginnner limit so that one waiting can change to paid.
        bc.beginner_limit = 3
        bc.save()
        update_waiting(bc.id)
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations), 5)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 2)
        self.assertEqual(len(mail.outbox), 1)

        # add the last 2
        bc.beginner_limit = 6
        bc.save()
        update_waiting(bc.id)
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations), 5)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 0)
        self.assertEqual(len(mail.outbox), 2)

    @patch('program_app.src.class_registration_helper.PaymentHelper.create_payment')
    def test_update_status_beginner_waiting_error(self, mock_payment):
        mock_payment.side_effect = self.payment_side_effect
        # set up beginner class to have wait list
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 2
        bc.beginner_wait_limit = 10
        bc.returnee_limit = 0
        bc.save()

        # add 2 students paid and one waiting
        user = User.objects.get(pk=2)
        # don't give the user a card therefore will be an error with card payment.
        ps = ['paid', 'paid', 'waiting']
        for i in range(3):
            s = Student.objects.get(pk=i + 2)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status=ps[i],
                                   idempotency_key=str(uuid.uuid4()),
                                   user=user)
            cr.save()

        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'wait')
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 1)
        self.assertEqual(len(registrations.filter(pay_status='start')), 0)

        # chang the beginnner limit so that one waiting can change to paid.
        bc.beginner_limit = 3
        bc.save()
        update_waiting(bc.id)
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations), 3)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 0)
        self.assertEqual(len(registrations.filter(pay_status='start')), 1)

    @patch('program_app.src.class_registration_helper.PaymentHelper.create_payment')
    def test_update_status_return_waiting(self, mock_payment):
        mock_payment.side_effect = self.payment_side_effect
        # set up beginner class to have wait list
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.beginner_wait_limit = 0
        bc.returnee_limit = 2
        bc.returnee_wait_limit = 10
        bc.save()

        # add 2 students paid and one waiting
        user = User.objects.get(pk=2)
        self.add_card(user)
        ps = ['paid', 'paid', 'waiting']
        for i in range(3):
            s = Student.objects.get(pk=i + 2)
            s.safety_class = "2023-06-05"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=False,
                                   pay_status=ps[i],
                                   idempotency_key=str(uuid.uuid4()),
                                   user=user)
            cr.save()

        # add 2 more to the wait list at the same time so they go together.
        user = User.objects.get(pk=3)
        self.add_card(user)
        ik = str(uuid.uuid4())
        for i in range(2):
            s = Student.objects.get(pk=i + 5)
            s.safety_class = "2023-06-05"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=False,
                                   pay_status='waiting',
                                   idempotency_key=ik,
                                   user=user)
            cr.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'wait')
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 3)

        # change wait  limit to 2 so that the class is full.
        bc.returnee_wait_limit = 2
        bc.save()
        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.event.state, 'full')

        # chang the beginnner limit so that one waiting can change to paid.
        bc.returnee_limit = 3
        bc.save()
        update_waiting(bc.id)
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations), 5)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 2)

        # add the last 2
        bc.returnee_limit = 6
        bc.save()
        update_waiting(bc.id)
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations), 5)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 0)

    def test_has_space_beginner(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'beginner'
        bc.beginner_limit = 5
        bc.returnee_limit = 0
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = None
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.assertEqual(self.crh.has_space(self.test_user, bc, 1, 0, 0), 'open')
        self.assertEqual(self.crh.has_space(self.test_user, bc, 3, 0, 0), 'full')
        bc.beginner_wait_limit = 3
        bc.save()
        self.assertEqual(self.crh.has_space(self.test_user, bc, 3, 0, 0), 'wait')

    def test_has_space_returnee(self):
        bc = BeginnerClass.objects.get(pk=1)
        bc.class_type = 'returnee'
        bc.beginner_limit = 0
        bc.returnee_limit = 5
        bc.save()
        for i in range(3):
            s = Student.objects.get(pk=i + 3)
            s.safety_class = "2021-05-31"
            s.save()
            cr = ClassRegistration(beginner_class=bc,
                                   student=s,
                                   new_student=True,
                                   pay_status='paid',
                                   idempotency_key=str(uuid.uuid4()))
            cr.save()
        self.assertEqual(self.crh.has_space(self.test_user, bc, 0, 0, 1), 'open')
        self.assertEqual(self.crh.has_space(self.test_user, bc, 0, 0, 3), 'full')
        bc.returnee_wait_limit = 3
        bc.save()
        self.assertEqual(self.crh.has_space(self.test_user, bc, 0, 0, 3), 'wait')
