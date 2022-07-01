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
        self.errors = []
        self.errors_codes = []
        self.error_dict = {
            'CVV_FAILURE': 'Payment Error: CVV',
            'CARD_DECLINED_VERIFICATION_REQUIRED':
                'Payment Error: Strong Authentication not supported at this time, please use a different card.',
            'GENERIC_DECLINE': 'Payment Error: Card Declined',
            'IDEMPOTENCY_KEY_REUSED': 'Retry error',
            'INVALID_EXPIRATION': 'Payment Error: Expiration Date',
            'NOT_FOUND': 'Object not found',
            '': 'Payment Error'
        }

    def handle_error(self, result, default_error):
        logging.error(result.errors)
        for error in result.errors:
            self.errors.append(self.error_dict.get(error.get('code', ''), default_error))
            self.errors_codes.append(error.get('code', ''))

