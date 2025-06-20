from django.template.loader import get_template

from _email.src import EmailMessage as EM
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EM):
    def contact_email(self, message):
        self.bcc.append(message.category.email)
        self.bcc.append(message.email)
        self.reply_to = [message.email, message.category.email]
        self.subject = f'WPA Contact Us {message.category.title}'
        self.body = get_template('contact_us/email/message.txt').render({'message': message})
        self.attach_alternative(get_template('contact_us/email/message.html').render({'message': message}), 'text/html')
        self.send()
