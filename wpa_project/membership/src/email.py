from django.template.loader import get_template

from student_app.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    # def confirm_notice(self, member):
    #     """ Send a notice to a member to let them know that their membership has been confirmed"""
    #
    #     self.get_email_address(member.student.user)
    #     d = {'name': f'{member.student.first_name} {member.student.last_name}', 'expire_date': member.expire_date}
    #     self.subject = 'Woodley Park Archers Membership Expiring'
    #     self.body = get_template('membership/email/expire_email.txt').render(d)
    #     self.attach_alternative(get_template('membership/email/expire_email.html').render(d), 'text/html')
    #     self.send()

    def expire_notice(self, member):
        """ Send a notice to a member to let them know that their membership is going to expire"""

        self.get_email_address(member.student.user)
        logger.warning(self.to)
        d = {'name': f'{member.student.first_name} {member.student.last_name}', 'expire_date': member.expire_date}
        self.subject = 'Woodley Park Archers Membership Expiring'
        self.body = get_template('membership/email/expire_email.txt').render(d)
        self.attach_alternative(get_template('membership/email/expire_email.html').render(d), 'text/html')
        self.send()


    # def payment_email_user(self, user, pay_dict):
    #     """ Takes information from the pay dict and emails it to the user. pay_dict = {line_items: string, total: int,
    #         receipt: url,} """
    #
    #     self.get_email_address(user)
    #     pay_dict['name'] = user.first_name
    #     pay_dict['line_items'] = self.line_items(pay_dict['line_items'])
    #     self.subject = 'Woodley Park Archers Payment Confirmation'
    #     self.body = get_template('student_app/email/payment_email.txt').render(pay_dict)
    #     self.attach_alternative(get_template('student_app/email/payment_email.html').render(pay_dict), 'text/html')
    #     self.send()