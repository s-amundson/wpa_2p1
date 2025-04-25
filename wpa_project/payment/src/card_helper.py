import uuid
import logging
from square.core.api_error import ApiError

from ..models import Card
from .square_helper import SquareHelper

logger = logging.getLogger(__name__)


class CardHelper(SquareHelper):
    def __init__(self, card=None):
        super().__init__()
        self.card = card

    def create_card_from_payment(self, customer, payment, is_default):
        return self.create_card_from_source(customer, payment.payment_id, is_default)

    def create_card_from_source(self, customer, source_id, is_default):
        idempotency_key = str(uuid.uuid4())
        try:
            result = self.client.cards.create(
                idempotency_key=idempotency_key,
                source_id=source_id,
                card={"customer_id": customer.customer_id}
            )
            if is_default:
                cards = customer.card_set.all().update(default=False)
            else:
                if len(customer.card_set.filter(default=True)) == 0:
                    is_default = True

            card = result.card
            logger.warning(card)
            self.card = Card.objects.create(
                bin=card.bin,
                card_brand=card.card_brand,
                card_type=card.card_type,
                card_id=card.id,
                cardholder_name=card.cardholder_name,
                customer=customer,
                default=is_default,
                enabled=card.enabled,
                exp_month=card.exp_month,
                exp_year=card.exp_year,
                fingerprint=card.fingerprint,
                last_4=card.last4,
                merchant_id=card.merchant_id,
                prepaid_type=card.prepaid_type,
                version=card.version
            )
            return self.card

        except ApiError as e:
            self.user = customer.user
            self.handle_error(e, 'cards.create', ik=idempotency_key, default_error='Card Create Error')
        return None

    def disable_card(self):
        try:
            result = self.client.cards.disable(self.card.card_id)
            sq_card = result.card
            self.card.enabled = sq_card.enabled
            if self.card.default:
                last_card = self.card.customer.card_set.filter(enabled=True).exclude(default=True).last()
                if last_card:
                    last_card.default = True
                    last_card.save()
            self.card.default = False
            self.card.save()
            return self.card
        except ApiError as e:  # pragma: no cover
            self.handle_error(e, 'cards.disable_card')
            return None

    def retrieve_card(self):
        try:
            result = self.client.cards.get(self.card.card_id)
            card = result.card
            self.card.bin = card.bin
            self.card.card_brand = card.card_brand
            self.card.card_type = card.card_type
            self.card.card_id = card.id
            self.card.cardholder_name = card.cardholder_name
            self.card.enabled = card.enabled
            self.card.exp_month = card.exp_month
            self.card.exp_year = card.exp_year
            self.card.fingerprint = card.fingerprint
            self.card.last_4 = card.last4
            self.card.merchant_id = card.merchant_id
            self.card.prepaid_type = card.prepaid_type
            self.card.version = card.version
            self.card.save()
            return self.card
        except ApiError as e:
            self.handle_error(e, 'cards.retrieve_card')
            return None
