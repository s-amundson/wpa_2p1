import logging
from django.conf import settings

from .square_helper import SquareHelper
from ..models import Card, PaymentLog

logger = logging.getLogger(__name__)


class PaymentHelper(SquareHelper):

    def __init__(self, user):
        super().__init__()
        self.payment = None
        self.user = user

    def create_payment(self, amount, category, donation, idempotency_key, note, source_id,
                       autocomplete=True, saved_card_id=0):
        # logging.debug(note)
        body = {
                "idempotency_key": idempotency_key,
                "amount_money": {"amount": amount * 100, "currency": "USD"},
                "autocomplete": autocomplete,
                "location_id": settings.SQUARE_CONFIG['location_id'],
                "note": note[:250]
            }
        if saved_card_id != 0:
            card = Card.objects.get(pk=saved_card_id)
            body['source_id'] = card.card_id
            body['customer_id'] = card.customer.customer_id
        else:
            body['source_id'] = source_id
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
            return self.payment

        elif result.is_error():
            self.handle_error(result, 'Payment Error')

        return None
