import uuid
import logging

from ..models import Card
from .square_helper import SquareHelper

logger = logging.getLogger(__name__)


class CardHelper(SquareHelper):
    def __init__(self, card=None):
        super().__init__()
        self.card = card

    def create_card_from_payment(self, customer, payment):
        return self.create_card_from_source(customer, payment.payment_id)

    def create_card_from_source(self, customer, source_id):
        idempotency_key = str(uuid.uuid4())
        result = self.client.cards.create_card(
            body={
                "idempotency_key": idempotency_key,
                "source_id": source_id,
                "card": {
                    "customer_id": customer.customer_id
                }
            }
        )
        if result.is_success():
            logging.debug(result.body)
            card = result.body['card']
            self.card = Card.objects.create(
                bin=card['bin'],
                card_brand=card['card_brand'],
                card_type=card['card_type'],
                card_id=card['id'],
                cardholder_name=card.get('cardholder_name', ''),
                customer=customer,
                enabled=card['enabled'],
                exp_month=card['exp_month'],
                exp_year=card['exp_year'],
                fingerprint=card['fingerprint'],
                last_4=card['last_4'],
                merchant_id=card['merchant_id'],
                prepaid_type=card['prepaid_type'],
                version=card.get('version', 0)
            )
            return self.card
        elif result.is_error():  # pragma: no cover
            logging.error(result.errors)
            self.handle_error(result, 'Card Create Error')
        return None

    def disable_card(self):
        result = self.client.cards.disable_card(
          card_id=self.card.card_id
        )
        if result.is_success():
            logging.debug(result.body)
            sq_card = result.body['card']
            self.card.enabled = sq_card['enabled']
            self.card.save()
            return self.card
        elif result.is_error():  # pragma: no cover
            self.handle_error(result, 'Card Disable Error')
        return None

    def retrieve_card(self):
        result = self.client.cards.retrieve_card(
            card_id=self.card.card_id
        )

        if result.is_success():
            logging.debug(result.body)
            card = result.body['card']
            self.card.bin = card['bin']
            self.card.card_brand = card['card_brand']
            self.card.card_type = card['card_type']
            self.card.card_id = card['id']
            self.card.cardholder_name = card.get('cardholder_name', '')
            self.card.enabled = card['enabled']
            self.card.exp_month = card['exp_month']
            self.card.exp_year = card['exp_year']
            self.card.fingerprint = card['fingerprint']
            self.card.last_4 = card['last_4']
            self.card.merchant_id = card['merchant_id']
            self.card.prepaid_type = card['prepaid_type']
            self.card.version = card.get('version', 0)
            self.card.save()
            return self.card
        elif result.is_error():  # pragma: no cover
            self.handle_error(result, 'Card Retrieve Error')
        return None
