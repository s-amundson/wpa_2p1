import uuid
import logging
from django.apps import apps
from django.conf import settings
from django.utils.datetime_safe import datetime
from square.client import Client

from ..models import PaymentLog, RefundLog
from student_app.models import StudentFamily
logger = logging.getLogger(__name__)


class SquareHelper:
    def __init__(self):
        # Create an instance of the API Client
        # and initialize it with the credentials
        # for the Square account whose assets you want to manage
        self.client = Client(
            access_token=settings.SQUARE_CONFIG['access_token'],
            environment=settings.SQUARE_CONFIG['environment'],
        )

    def comp_response(self, note, amount):
        payment = {'approved_money': {'amount': amount},
                    'created_at': '2021-06-06T00:24:48.978Z',
                    'id': None,
                    'location_id': 'SVM1F73THA9W6',
                    'note': note,
                    'order_id': None,  # datetime.now().format('%Y%m%d%H%M%S%f'),
                    'receipt_url': None,
                    'source_type': None,
                    'status': 'comped',
                    'total_money': amount}
        if amount == 0:
            payment['status'] = 'paid'
        return payment

    def line_item(self, name, quantity, amount):
        # square requires amount in pennies
        l = {'name': name,
             'quantity': str(quantity),
             'base_price_money': {'amount': amount * quantity * 100,
                                  'currency': 'USD'},
             }
        return l

    def log_payment(self, request, square_response, create_date=None):
        if create_date is None:
            create_date = datetime.strptime(square_response['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        log = PaymentLog.objects.create(user=request.user,
                                        student_family=StudentFamily.objects.filter(user=request.user)[0],
                                        checkout_created_time=create_date,
                                        db_model=request.session.get('payment_db', None),
                                        description=square_response['note'],
                                        location_id=square_response['location_id'],
                                        idempotency_key=request.session['idempotency_key'],
                                        order_id=square_response['order_id'],
                                        payment_id=square_response['id'],
                                        receipt=square_response['receipt_url'],
                                        source_type=square_response['source_type'],
                                        status=square_response['status'],
                                        total_money=square_response['approved_money']['amount'],
                                        )
        # TODO email receipt if exists

        if request.session.get('payment_db', None) is not None:
            pdb = request.session['payment_db']
            m = apps.get_model(app_label=pdb[0], model_name=pdb[1])
            records = m.objects.filter(idempotency_key=request.session['idempotency_key'])
            for record in records:
                record.pay_status = 'paid'
                record.save()

    def log_refund(self, square_response, payment_log):
        # refund = square_response['refund']
        RefundLog.objects.create(amount=square_response['amount_money']['amount'],
                                 created_time=datetime.strptime(square_response['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                                 location_id=square_response['location_id'],
                                 order_id=square_response['order_id'],
                                 payment_id=square_response['payment_id'],
                                 processing_fee=square_response.get('processing_fee', None),
                                 refund_id=square_response['id'],
                                 status=square_response.get('status', None)
                                 )

    def payment_error(self, request):
        """ reset idempotency_key and increment payment_error count"""

        payment_error = request.session.get('payment_error', 0)
        if payment_error >= 2:  # only allow 3 tries
            return False
        request.session['payment_error'] = payment_error + 1

        if request.session.get('payment_db', None) is not None:
            ik = str(uuid.uuid4())
            pdb = request.session['payment_db']
            m = apps.get_model(app_label=pdb[0], model_name=pdb[1])
            records = m.objects.filter(idempotency_key=request.session['idempotency_key'])
            for record in records:
                record.idempotency_key = ik
                record.save()
            request.session['idempotency_key'] = ik
            logging.debug(f'ik = {ik}')
        return True

    def process_payment(self, idempotency_key, sq_token, note, amount):
        result = self.client.payments.create_payment(
            body={
                "source_id": sq_token,
                "idempotency_key": idempotency_key,
                "amount_money": amount,
                "autocomplete": True,
                "location_id": settings.SQUARE_CONFIG['location_id'],
                "note": note
            }
        )
        square_response = result.body.get('payment', {'payment': None})
        if result.is_success():
            square_response['error'] = []
        elif result.is_error():
            square_response['error'] = result.errors

        return square_response

    def refund_payment(self, idempotency_key, amount):
        """ does either a full or partial refund. """
        try:
            log = PaymentLog.objects.get(idempotency_key=idempotency_key)
        except PaymentLog.DoesNotExist:
            return {'status': "FAIL"}

        if log.status == 'comped':  # payment was comped therefore no refund
            log.status = 'refund'
            log.save()
            return {'status': "SUCCESS", 'error': ''}
        elif log.status == 'refund':
            rl = RefundLog.objects.filter(payment_id=log.payment_id)
            refunded_amount = 0
            for r in rl:
                refunded_amount += r.amount
            logging.debug(refunded_amount)
            if log.total_money <= refunded_amount:  # check if only partial refund was applied
                return {'status': 'error', 'error': 'Previously refunded'}
        result = self.client.refunds.refund_payment(
            body={"idempotency_key": str(uuid.uuid4()),
                  "amount_money": {'amount': amount * 100, 'currency': 'USD'},
                  "payment_id": log.payment_id
                  })
        square_response = result.body.get('refund', {'refund': None})
        if result.is_success():
            square_response['error'] = ""
            log.status = 'refund'
            log.save()
            self.log_refund(square_response, log)
        elif result.is_error():
            square_response['status'] = 'error'
            square_response['error'] = result.errors
        return square_response
