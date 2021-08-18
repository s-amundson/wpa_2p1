from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

# from wpa_project.student_app.models import ClassRegistration
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.test_emails = ["EmilyNConlan@einrot.com", "RosalvaAHall@superrito.com", "CharlesNWells@einrot.com",
                            "RicardoRHoyt@jourrapide.com", "RicardoRHoyt@Ricardo.com"]

    def get_email_address(self, user):
        if settings.EMAIL_DEBUG:
            self.to = settings.EMAIL_DEBUG_ADDRESSES
        else:
            self.to = [EmailAddress.objects.get_primary(user)]
            if self.to in self.test_emails:
                self.to = settings.EMAIL_DEBUG_ADDRESSES

    def line_items(self, line_items):
        for line in line_items:
            bpm = line['base_price_money']
            line['amount'] = bpm['amount']/100  # convert to dollars from cents
            line['cost'] = int(line['quantity']) * line['amount']
            del line['base_price_money']
        return line_items

    def payment_email_user(self, user, pay_dict):
        """ Takes information from the pay dict and emails it to the user. pay_dict = {line_items: string, total: int,
            receipt: url,} """

        self.get_email_address(user)
        pay_dict['name'] = user.first_name
        pay_dict['line_items'] = self.line_items(pay_dict['line_items'])
        self.subject = 'Woodley Park Archers Payment Confirmation'
        self.body = get_template('student_app/email/payment_email.txt').render(pay_dict)
        self.attach_alternative(get_template('student_app/email/payment_email.html').render(pay_dict), 'text/html')
        self.send()

    def refund_email(self, user, donation=False):
        self.get_email_address(user)
        d = {'name': user.first_name, 'donation': donation}
        self.subject = 'Woodley Park Archers Refund Confirmation'
        self.body = get_template('student_app/email/refund_email.txt').render(d)
        self.attach_alternative(get_template('student_app/email/refund_email.html').render(d), 'text/html')
        self.send()

    # def release_email(self, registration, pdf):
    #     cr = ClassRegistration.objects.get(pk=registration)
    #     users = cr.student.student_family.user.all()
    #     logging.debug(users)
    #     self.get_email_address(users[0])
    #     # TODO set to student if student is user.
    #     self.subject = ""
