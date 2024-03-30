from django.template.loader import get_template

from _email.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    def expire_notice(self, member):
        """ Send a notice to a member to let them know that their membership is going to expire"""

        self.get_email_address(member.student.user)
        logger.warning(self.to)
        d = {'name': f'{member.student.first_name} {member.student.last_name}', 'expire_date': member.expire_date}
        self.subject = 'Woodley Park Archers Membership Expiring'
        self.body = get_template('membership/email/expire_email.txt').render(d)
        self.attach_alternative(get_template('membership/email/expire_email.html').render(d), 'text/html')
        self.send()
