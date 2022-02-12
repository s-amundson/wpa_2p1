from django.template.loader import get_template

from student_app.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    def contact_email(self, message):
        self.bcc_from_users(message.category.recipients.all())
        self.bcc.append(message.email)
        self.subject = f'WPA Contact Us {message.category.title}'
        self.body = get_template('contact_us/email/message.txt').render({'message': message})
        self.attach_alternative(get_template('contact_us/email/message.html').render({'message': message}), 'text/html')
        self.send()
