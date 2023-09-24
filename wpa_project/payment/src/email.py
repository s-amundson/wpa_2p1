from django.template.loader import get_template

from student_app.src import EmailMessage as StudentEmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(StudentEmailMessage):
    def line_items(self, line_items):
        for line in line_items:
            line['cost'] = int(line['quantity']) * line['amount_each']
        return line_items

    def payment_email_user(self, user, pay_dict):
        """ Takes information from the pay dict and emails it to the user. pay_dict = {line_items: string, total: int,
            receipt: url,} """

        self.get_email_address(user)
        pay_dict['name'] = user.student_set.last().first_name
        pay_dict['line_items'] = self.line_items(pay_dict['line_items'])
        self.subject = 'Woodley Park Archers Payment Confirmation'
        self.body = get_template('payment/email/payment_email.txt').render(pay_dict)
        self.attach_alternative(get_template('payment/email/payment_email.html').render(pay_dict), 'text/html')
        self.send()

    def payment_error_email(self, user, message=None):
        self.get_email_address(user)
        d = {'message': message, 'name': user.student_set.last().first_name}
        self.subject = 'Woodley Park Archers Error with Payment'
        self.body = get_template('payment/email/payment_error_email.txt').render(d)
        self.attach_alternative(get_template('payment/email/payment_error_email.html').render(d),
                                'text/html')
        self.send()

    def refund_email(self, user, donation=False):
        self.get_email_address(user)
        d = {'name': user.student_set.last().first_name, 'donation': donation}
        self.subject = 'Woodley Park Archers Refund Confirmation'
        self.body = get_template('payment/email/refund_email.txt').render(d)
        self.attach_alternative(get_template('payment/email/refund_email.html').render(d), 'text/html')
        self.send()

    def refund_canceled_email(self, user, event, message=''):
        self.get_email_address(user)
        d = {'name': user.student_set.last().first_name, 'event': event, 'message': message}
        self.subject = 'Woodley Park Archers Cancellation'
        self.body = get_template('payment/email/refund_canceled_email.txt').render(d)
        self.attach_alternative(get_template('payment/email/refund_canceled_email.html').render(d), 'text/html')
        self.send()

