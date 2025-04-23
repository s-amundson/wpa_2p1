import uuid
import logging
from django.utils import timezone
from square.core.api_error import ApiError

from .square_helper import SquareHelper
from ..models import PaymentLog, RefundLog
from event.models import VolunteerRecord
logger = logging.getLogger(__name__)


class RefundHelper(SquareHelper):
    def refund_with_idempotency_key(self, idempotency_key, amount):
        """ does either a full or partial refund. Takes and idempotency_key and amount as arguments, Looks up the log
        then calls refund_payment"""
        log = PaymentLog.objects.filter(idempotency_key=idempotency_key).last()
        if log is None:
            return {'status': "FAIL", 'error': 'Record does not exist'}
        return self.refund_payment(log, amount)

    def refund_entire_payment(self, log):
        return self.refund_payment(log, log.total_money + log.volunteer_points * 100)

    def refund_payment(self, log, amount):
        """ does either a full or partial refund. """
        refund_points = 0
        if log.volunteer_points:
            logger.warning(f'volunteer points:{log.volunteer_points}, amount: {amount}')
            vr = VolunteerRecord.objects.filter(student=log.user.student_set.last(),
                                                volunteer_points=0 - log.volunteer_points).last()
            logger.warning(log.volunteer_points >= amount/100)
            if log.volunteer_points >= amount/100:
                vr.volunteer_points += amount/100
                log.volunteer_points -= amount/100
                RefundLog.objects.create(amount=0,
                                         created_time=timezone.now(),
                                         location_id='volunteer_points',
                                         order_id=None,
                                         payment_id=log.payment_id,
                                         refund_id=vr.id,
                                         status='SUCCESS',
                                         volunteer_points=amount
                                         )
                log.status = 'refund'
                log.save()
                vr.save()
                return {'status': "SUCCESS", 'error': ''}
            else:
                amount -= log.volunteer_points * 100
                refund_points = log.volunteer_points
                vr.volunteer_points = 0
            vr.save()
        logging.warning(log.status)
        if log.status in ['comped']:
            # payment was comped therefore no square refund,
            log.status = 'refund'
            log.save()
            return {'status': "SUCCESS", 'error': ''}
        elif log.status in ['refund', 'PENDING']:
            rl = RefundLog.objects.filter(payment_id=log.payment_id)
            refunded_amount = 0
            for r in rl:
                refunded_amount += r.amount
            if log.total_money <= refunded_amount:  # check if only partial refund was applied
                return {'status': 'error', 'error': 'Previously refunded'}

        idempotency_key = uuid.uuid4()
        try:
            result = self.client.refunds.refund_payment(
                idempotency_key=str(idempotency_key),
                amount_money={'amount': amount, 'currency': 'USD'},
                payment_id=log.payment_id
            )
            log.status = 'refund'
            log.save()
            RefundLog.objects.create(amount=result.refund.amount_money.amount,
                                     created_time=result.refund.created_at,
                                     location_id=result.refund.location_id,
                                     order_id=result.refund.order_id,
                                     payment_id=result.refund.payment_id,
                                     processing_fee=result.refund.processing_fee,
                                     refund_id=result.refund.id,
                                     status=result.refund.status,
                                     volunteer_points=refund_points,
                                     )
            return result

        except ApiError as e:
            self.handle_error(e, 'refunds.refund_payment')
        return None
