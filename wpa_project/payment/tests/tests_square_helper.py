import logging
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps

from ..models import PaymentLog
from ..src import SquareHelper

logger = logging.getLogger(__name__)


class TestsSquareHelper(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=2)
        self.client.force_login(self.test_user)
        session = self.client.session
        session['idempotency_key'] = str(uuid.uuid4())
        session['line_items'] = [{'name': 'Class on None student id: 1',
                                  'quantity': '1', 'base_price_money': {'amount': 500, 'currency': 'USD'}}]
        session.save()

    def test_refund_bypass(self):
        response = self.client.post(reverse('payment:process_payment'),
                                    {'bypass': ''}, secure=True)
        self.assertTemplateUsed('student_app/message.html')
        pl = PaymentLog.objects.all()
        self.assertEqual(len(pl), 1)

        sh = SquareHelper()
        rp = sh.refund_payment(pl[0].idempotency_key, 500)
        pl = PaymentLog.objects.get(pk=1)
        self.assertEqual(pl.status, 'refund')
        self.assertEqual(rp, {'status': "SUCCESS", 'error': ''})
        logging.debug(pl.total_money)

        rp = sh.refund_payment(pl.idempotency_key, 500)
        self.assertEqual(rp['error'][0]['code'], 'VALUE_EMPTY')
        self.assertIsNone(rp['refund'])

        pl.total_money = 0
        pl.save()
        rp = sh.refund_payment(pl.idempotency_key, 500)
        self.assertEqual(rp, {'status': 'error', 'error': 'Previously refunded'})

    def test_square_helper_refund_payment_error(self):
        rp = SquareHelper().refund_payment(str(uuid.uuid4()), 1000)
        self.assertEqual(rp, {'status': "FAIL"})
