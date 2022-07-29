import logging
import time
import uuid

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..forms import PaymentForm
from ..models import RefundLog
from ..src import RefundHelper

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

    def test_square_helper_refund_payment_error(self):
        rp = RefundHelper().refund_with_idempotency_key(str(uuid.uuid4()), 1000)
        self.assertEqual(rp, {'status': "FAIL", 'error': 'Record does not exist'})

    def test_square_helper_refund_payment(self):
        pf = PaymentForm(user=self.test_user)
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
            'source_id': 'cnon:card-nonce-ok'
        }
        pf.process_payment(str(uuid.uuid4()))
        logging.debug(pf.log)

        time.sleep(5)

        refund = RefundHelper()
        refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].status, 'PENDING')

        time.sleep(5)
        refund = RefundHelper()
        error_refund = refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        self.assertEqual(len(rl), 1)
        self.assertEqual(error_refund['status'], 'error')


    def test_refund_amount_zero(self):
        pf = PaymentForm(user=self.test_user)
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
            'source_id': 'no-payment'
        }
        pf.process_payment(str(uuid.uuid4()))
        logging.debug(pf.log)
        time.sleep(5)

        refund = RefundHelper()
        refund.refund_entire_payment(pf.log)
        rl = RefundLog.objects.all()
        logging.debug(len(rl))
        self.assertEqual(len(rl), 0)
        self.assertEqual(pf.log.status, 'refund')
