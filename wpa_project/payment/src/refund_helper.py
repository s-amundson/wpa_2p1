import uuid
import logging

from .square_helper import SquareHelper
from ..models import PaymentLog, RefundLog

logger = logging.getLogger(__name__)


class RefundHelper(SquareHelper):
    def log_refund(self, square_response, payment_log):
        # refund = square_response['refund']
        RefundLog.objects.create(amount=square_response['amount_money']['amount'],
                                 created_time=square_response['created_at'],
                                 location_id=square_response['location_id'],
                                 order_id=square_response['order_id'],
                                 payment_id=square_response['payment_id'],
                                 processing_fee=square_response.get('processing_fee', None),
                                 refund_id=square_response['id'],
                                 status=square_response.get('status', None)
                                 )

    def refund_with_idempotency_key(self, idempotency_key, amount):
        """ does either a full or partial refund. Takes and idempotency_key and amount as arguments, Looks up the log
        then calls refund_payment"""
        try:
            log = PaymentLog.objects.get(idempotency_key=idempotency_key)
        except PaymentLog.DoesNotExist:
            return {'status': "FAIL"}
        return self.refund_payment(log, amount)

    def refund_entire_payment(self, log):
        return self.refund_payment(log, log.total_money)

    def refund_payment(self, log, amount):
        """ does either a full or partial refund. """

        if log.status == 'comped':  # payment was comped therefore no refund
            log.status = 'refund'
            log.save()
            return {'status': "SUCCESS", 'error': ''}
        elif log.status in ['refund', 'PENDING']:
            rl = RefundLog.objects.filter(payment_id=log.payment_id)
            refunded_amount = 0
            for r in rl:
                refunded_amount += r.amount
            # logging.debug(refunded_amount)
            # logging.debug(log.total_money)
            if log.total_money <= refunded_amount:  # check if only partial refund was applied
                return {'status': 'error', 'error': 'Previously refunded'}
        result = self.client.refunds.refund_payment(
            body={"idempotency_key": str(uuid.uuid4()),
                  "amount_money": {'amount': amount, 'currency': 'USD'},
                  "payment_id": log.payment_id
                  })
        square_response = result.body.get('refund', {'refund': None})
        if result.is_success():
            square_response['error'] = ""
            log.status = 'refund'
            log.save()
            self.log_refund(square_response, log)
        elif result.is_error():  # pragma: no cover
            square_response['status'] = 'error'
            logging.debug(result.errors)
            square_response['error'] = result.errors
        return square_response
