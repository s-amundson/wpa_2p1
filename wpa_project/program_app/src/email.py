from django.template.loader import get_template

from student_app.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    def status_email(self, class_list, staff):
        """Takes a list containing {'class': [beginner_class], 'instructors': [students], 'staff': [students]}"""
        self.bcc_from_users(staff)

        self.subject = f'WPA Class Status {class_list[0]["class"].class_date.date()}'
        logging.debug(class_list)

        self.body = get_template('program_app/email/status_email.txt').render({'class_list': class_list})
        self.attach_alternative(get_template('program_app/email/status_email.html').render({'class_list': class_list}),
                                'text/html')
        self.send()
