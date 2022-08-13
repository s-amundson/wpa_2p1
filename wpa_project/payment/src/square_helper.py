import logging
from django.conf import settings
from square.client import Client
from ..models import PaymentErrorLog

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
        self.error_log = None
        self.testing = settings.SQUARE_TESTING
        self.user = None

    def log_error(self, category, error, idempotency_key, api):
        self.error_log = PaymentErrorLog.objects.create(
            user=self.user,
            category=category,
            error_code=error,
            idempotency_key=idempotency_key,
            api=api
        )

    def handle_error(self, result, default_error):
        logging.error(result.errors)
        for error in result.errors:
            self.errors.append(self.error_dict.get(error.get('code', ''), default_error))
            self.errors_codes.append(error.get('code', ''))

