from django.template.loader import get_template

from student_app.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):

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
        self.body = get_template('payment/email/payment_email.txt').render(pay_dict)
        self.attach_alternative(get_template('payment/email/payment_email.html').render(pay_dict), 'text/html')
        self.send()

    def refund_email(self, user, donation=False):
        self.get_email_address(user)
        d = {'name': user.first_name, 'donation': donation}
        self.subject = 'Woodley Park Archers Refund Confirmation'
        self.body = get_template('payment/email/refund_email.txt').render(d)
        self.attach_alternative(get_template('payment/email/refund_email.html').render(d), 'text/html')
        self.send()

    def refund_canceled_email(self, user, event):
        self.get_email_address(user)
        d = {'name': user.first_name, 'event': event}
        self.subject = 'Woodley Park Archers Cancellation'
        self.body = get_template('payment/email/refund_canceled_email.txt').render(d)
        self.attach_alternative(get_template('payment/email/refund_canceled_email.html').render(d), 'text/html')
        self.send()

