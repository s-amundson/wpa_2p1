import logging
import time
import uuid

from django.test import TestCase, Client, tag
from django.contrib.auth import get_user_model

from ..forms import PaymentForm
from ..models import RefundLog
from ..src import RefundHelper
from event.models import VolunteerRecord

logger = logging.getLogger(__name__)


class TestsRefund(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = get_user_model()

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        session = self.client.session
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [{'name': 'Class on None student: test_user',
                                  'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
        session.save()
    # @tag('temp')
    def test_square_helper_refund_payment_error(self):
        rp = RefundHelper().refund_with_idempotency_key(str(uuid.uuid4()), 1000)
        self.assertEqual(rp, {'status': "FAIL", 'error': 'Record does not exist'})

    # @tag('temp')
    def test_square_helper_refund_payment(self):
        pf = PaymentForm(user=self.test_user, initial={'amount': 5, 'category': 'donation'}, client_ip='')
        pf.cleaned_data = {
            'amount': 5,
            'card': '0',
            'category': 'donation',
            'donation': 0,
            'donation_note': '',
            'items': {
                'name': 'widget',
                'quantity': '1',
                'amount_each': 5},
            'save_card': False,
            'source_id': 'cnon:card-nonce-ok',
            'email': ''
        }
        pf.process_payment(str(uuid.uuid4()))

        time.sleep(5)

        refund = RefundHelper()
        refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertIn(rl[0].status, ['PENDING', 'SUCCESS'])

        time.sleep(5)
        refund = RefundHelper()
        error_refund = refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(error_refund['status'], 'error')

    # @tag('temp')
    def test_refund_amount_zero(self):
        pf = PaymentForm(user=self.test_user, initial={'amount': 0, 'category': 'donation'}, client_ip='')
        pf.cleaned_data = {
            'amount': 0,
            'card': '0',
            'category': 'donation',
            'donation': 0,
            'donation_note': '',
            'items': {
                'name': 'widget',
                'quantity': '1',
                'amount_each': 0},
            'save_card': False,
            'source_id': 'no-payment',
            'email': ''
        }
        pf.process_payment(str(uuid.uuid4()))
        time.sleep(5)

        refund = RefundHelper()
        refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 0)
        self.assertEqual(pf.log.status, 'refund')

    # @tag('temp')
    def test_refund_volunteer_points(self):
        # set up initial points
        student = self.test_user.student_set.last()
        vr = VolunteerRecord.objects.create(
            student=student,
            volunteer_points=6.5
        )

        # create a payment to charge against points
        pf = PaymentForm(user=self.test_user, initial={'amount': 5, 'category': 'donation'}, client_ip='')
        pf.save_log(uuid.uuid4(), 'refund volunteer points', 'volunteer points', 5)
        logger.warning(pf.log)
        vr = VolunteerRecord.objects.create(
            student=self.test_user.student_set.last(),
            volunteer_points=-5
        )
        self.assertEqual(VolunteerRecord.objects.get_family_points(student.student_family), 1.5)

        refund = RefundHelper()
        refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(pf.log.status, 'refund')
        vr = VolunteerRecord.objects.filter(student=student)
        self.assertEqual(len(vr), 2)
        self.assertEqual(VolunteerRecord.objects.get_family_points(student.student_family), 6.5)

    # @tag('temp')
    def test_square_helper_refund_payment_and_points(self):
        # set up initial points
        student = self.test_user.student_set.last()
        vr = VolunteerRecord.objects.create(
            student=student,
            volunteer_points=2.5
        )

        pf = PaymentForm(user=self.test_user, initial={'amount': 5, 'category': 'donation'}, client_ip='')
        pf.cleaned_data = {
            'amount': 5,
            'card': '0',
            'category': 'donation',
            'donation': 0,
            'donation_note': '',
            'items': {
                'name': 'widget',
                'quantity': '1',
                'amount_each': 5},
            'save_card': False,
            'source_id': 'cnon:card-nonce-ok',
            'volunteer_points': 2,
            'email': ''
        }
        pf.process_payment(str(uuid.uuid4()))
        self.assertEqual(VolunteerRecord.objects.get_family_points(student.student_family), 0.5)
        logger.warning(f'total money:{pf.log.total_money}, volunteer_points: {pf.log.volunteer_points}')
        time.sleep(5)

        refund = RefundHelper()
        refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertIn(rl[0].status, ['PENDING', 'SUCCESS'])
        self.assertEqual(VolunteerRecord.objects.get_family_points(student.student_family), 2.5)
