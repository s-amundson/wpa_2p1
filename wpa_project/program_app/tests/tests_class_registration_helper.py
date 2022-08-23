import logging
import uuid
from django.core import mail
from django.test import TestCase, Client
from django.conf import settings

from ..src import ClassRegistrationHelper
from ..models import BeginnerClass, ClassRegistration
from ..tasks import update_waiting
from student_app.models import Student, User
from payment.models import Card, Customer

logger = logging.getLogger(__name__)


class TestsClassRegistrationHelper(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crh = ClassRegistrationHelper()

    def add_card(self, user):
        customer = Customer.objects.create(user=user,
                                           customer_id="9Z9Q0D09F0WMV0FHFA2QMZH8SC",
                                           created_at="2022-05-30T19:50:46Z",
                                           creation_source="THIRD_PARTY",
                                           updated_at="2022-05-30T19:50:46Z")
        card = Card.objects.create(
            bin=411111,
            card_brand="VISA",
            card_id="ccof:8sLQqf1boPfmwDKI4GB",
            card_type="CREDIT",
            cardholder_name="",
            customer=customer,
            default=1,
            enabled=1,
            exp_month=11,
            exp_year=2022,
            fingerprint="sq-1-npXvWJT5AhTtISQwBYohbA8kkQ24CyPCN6G6kP_6Bm_K2KPYsT1y_1xKUhvAnMIzfA",
            # id=1,
            last_4=1111,
            merchant_id="TYXMY2T8CN2PK",
            prepaid_type="NOT_PREPAID",
            version=0)
        return card

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        settings.SQUARE_TESTING = True

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
        self.assertEqual(bc.state, 'full')

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
        self.assertEqual(bc.state, 'full')

        #  remove student
        cr = ClassRegistration.objects.last()
        cr.pay_status = 'refund'
        cr.save()

        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')

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
        self.assertEqual(bc.state, 'open')

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
        self.assertEqual(bc.state, 'full')

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
        self.assertEqual(bc.state, 'full')

        #  remove student
        cr = ClassRegistration.objects.last()
        cr.pay_status = 'refund'
        cr.save()

        self.crh.update_class_state(bc)
        bc = BeginnerClass.objects.get(pk=1)
        self.assertEqual(bc.state, 'open')

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
        self.assertEqual(bc.state, 'open')

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
        self.assertEqual(bc.state, 'full')

    def test_update_status_beginner_waiting(self):
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
        self.assertEqual(bc.state, 'wait')
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 3)

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

    def test_update_status_beginner_waiting_error(self):
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
        self.assertEqual(bc.state, 'wait')
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


    def test_update_status_return_waiting(self):
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
        self.assertEqual(bc.state, 'wait')
        registrations = ClassRegistration.objects.filter(beginner_class=bc)
        self.assertEqual(len(registrations.filter(pay_status='waiting')), 3)

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
