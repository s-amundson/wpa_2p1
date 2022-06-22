import uuid
import logging
from django.apps import apps
from django.conf import settings
from django.utils.datetime_safe import datetime
from square.client import Client
import django.dispatch

from ..models import Card, Customer, DonationLog, PaymentLog, PaymentErrorLog, RefundLog
from student_app.models import Student
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
        # self.square_response = {'payment': None}
        # self.donation_amount = 0
        # self.donation_note = ''
        #
        # error_signal = django.dispatch.Signal()


class CardHelper(SquareHelper):
    def __init__(self, card=None):
        super().__init__()
        self.card = card

    def create_card_from_payment(self, customer, payment):
        idempotency_key = str(uuid.uuid4())
        result = self.client.cards.create_card(
            body={
                "idempotency_key": idempotency_key,
                "source_id": payment.payment_id,
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
        elif result.is_error():
            logging.error(result.errors)
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
        elif result.is_error():
            logging.error(result.errors)
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
        elif result.is_error():
            logging.error(result.errors)
        return None


class CustomerHelper(SquareHelper):
    def __init__(self, user):
        super().__init__()
        self.customer = None
        self.user = user

    def create_customer(self):
        idempotency_key = str(uuid.uuid4())
        result = self.client.customers.create_customer(
          body={
            "idempotency_key": idempotency_key,
            "email_address": self.user.email
          }
        )
        if result.is_success():
            # logging.debug(result.body)
            customer = result.body['customer']
            self.customer = Customer.objects.create(
                customer_id=customer['id'],
                created_at=customer['created_at'],
                creation_source=customer['creation_source'],
                updated_at=customer['updated_at'],
                user=self.user,
                version=customer['version']
            )
            return self.customer
        elif result.is_error():
            logging.error(result.errors)
        return None

    def delete_customer(self):
        c = Customer.objects.get(user=self.user)
        result = self.client.customers.delete_customer(
            customer_id=c.customer_id,
        )

        if result.is_success():
            logging.debug(result.body)
        elif result.is_error():
            logging.error(result.errors)

    def retrieve_customer(self):
        self.customer = Customer.objects.get(user=self.user)
        result = self.client.customers.retrieve_customer(
            customer_id=self.customer.customer_id,
        )

        if result.is_success():
            customer = result.body['customer']
            self.customer.created_at = customer['created_at']
            self.customer.creation_source = customer['creation_source']
            self.customer.updated_at = customer['updated_at']
            self.customer.user = self.user
            self.customer.version = customer['version']
            return self.customer
        elif result.is_error():
            logging.error(result.errors)
        return None


class Refund(SquareHelper):
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

        if log.source_type == 'comped' and log.status == 'COMPLETED':  # payment was comped therefore no refund
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
                  "amount_money": {'amount': amount, 'currency': 'USD'},
                  "payment_id": log.payment_id
                  })
        square_response = result.body.get('refund', {'refund': None})
        logging.debug(square_response)
        logging.debug(result)
        if result.is_success():
            square_response['error'] = ""
            log.status = 'refund'
            log.save()
            self.log_refund(square_response, log)
        elif result.is_error():
            square_response['status'] = 'error'
            logging.debug(result.errors)
            logging.debug(type(result.errors))
            square_response['error'] = result.errors
        return square_response
