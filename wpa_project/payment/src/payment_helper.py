import logging
from django.conf import settings
from square.core.api_error import ApiError

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
        if kwargs.get('saved_card_id', 0) != 0:
            card = Card.objects.get(pk=kwargs.get('saved_card_id'))
            # body['source_id'] = card.card_id
            customer_id = card.customer.customer_id
            source_id = card.card_id
        else:
            customer_id = None

        if PaymentLog.objects.filter(idempotency_key=idempotency_key):  # pragma: no cover
            return PaymentLog.objects.filter(idempotency_key=idempotency_key).last(), True

        try:
            result = self.client.payments.create(
                source_id=source_id,
                idempotency_key=str(idempotency_key),
                # amount_money={"amount": 1000, "currency": "USD"},
                amount_money={"amount": amount * 100, "currency": "USD"},
                autocomplete=kwargs.get('autocomplete', True),
                customer_id=customer_id,
                location_id=settings.SQUARE_CONFIG['location_id'],
                # reference_id="123456",
                note=note[:250],
            )

            self.payment = PaymentLog.objects.create(
                category=category,
                checkout_created_time=result.payment.created_at,
                description=note[:250],  # database set to 255 characters
                donation=donation * 100,  # storing pennies in the database
                idempotency_key=idempotency_key,
                location_id=result.payment.location_id,
                order_id=result.payment.order_id,
                payment_id=result.payment.id,
                receipt=result.payment.receipt_url,
                source_type=result.payment.source_type,
                status=result.payment.status,
                total_money=result.payment.approved_money.amount,
                user=self.user
            )
            return self.payment, False
        except ApiError as e:
            self.handle_error(e, 'payments.create_payment', ik=idempotency_key)
            if not kwargs.get('live', False):
                # email the user since the user didn't directly initiate this payment
                EmailMessage().payment_error_email(self.user, self.errors[0])
        return None, False
