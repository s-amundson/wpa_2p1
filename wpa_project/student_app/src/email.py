from allauth.account.models import EmailAddress
from allauth.account.managers import EmailAddressManager
from django.core.mail import EmailMessage
import logging
logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_email = 'from@example.com'

    def payment_email_user(self, user):
        logging.debug(user)
        self.to = [EmailAddress.objects.get_primary(user)]
        self.subject = 'Woodley Park Archers Payment Confirmation'
        self.body = f'Thank you for your payment. '
        self.send()
