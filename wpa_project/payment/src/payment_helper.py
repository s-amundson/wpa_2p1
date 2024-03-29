import logging
from django.conf import settings

from .square_helper import SquareHelper
from ..models import Card, PaymentLog
from .email import EmailMessage

logger = logging.getLogger(__name__)


class PaymentHelper(SquareHelper):

    def __init__(self, user):
        super().__init__()
        self.payment = None
        self.user = user

    def create_payment(self, amount, category, donation, idempotency_key, note, source_id, **kwargs):
        body = {
                "idempotency_key": str(idempotency_key),
                "amount_money": {"amount": amount * 100, "currency": "USD"},
                "autocomplete": kwargs.get('autocomplete', True),
                "location_id": settings.SQUARE_CONFIG['location_id'],
                "note": note[:250]
            }
        if kwargs.get('saved_card_id', 0) != 0:
            card = Card.objects.get(pk=kwargs.get('saved_card_id'))
            body['source_id'] = card.card_id
            body['customer_id'] = card.customer.customer_id
        else:
            body['source_id'] = source_id

        if PaymentLog.objects.filter(idempotency_key=idempotency_key):  # pragma: no cover
            return PaymentLog.objects.filter(idempotency_key=idempotency_key).last(), True
        result = self.client.payments.create_payment(
            body=body
        )
        response = result.body.get('payment', {'payment': None})

        if result.is_success():
            self.payment = PaymentLog.objects.create(
                category=category,
                checkout_created_time=response['created_at'],
                description=note[:250],  # database set to 255 characters
                donation=donation * 100,  # storing pennies in the database
                idempotency_key=idempotency_key,
                location_id=response['location_id'],
                order_id=response['order_id'],
                payment_id=response['id'],
                receipt=response['receipt_url'],
                source_type=response['source_type'],
                status=response['status'],
                total_money=response['approved_money']['amount'],
                user=self.user
            )
            return self.payment, False

        elif result.is_error():
            logger.warning(result.errors)
            for error in result.errors:
                self.log_error(category, error.get('code', 'unknown_error'), idempotency_key, 'payments.create_payment')
            self.handle_error(result, 'Payment Error')
            if not kwargs.get('live', False):
                # email the user since the user didn't directly initiate this payment
                EmailMessage().payment_error_email(self.user, self.errors[0])
        return None, False
