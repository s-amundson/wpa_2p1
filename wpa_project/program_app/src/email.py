from django.template.loader import get_template

from student_app.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    def beginner_reminder(self, beginner_class, students):
        self.bcc_from_students(students)
        self.subject = f'WPA Class Reminder {beginner_class.class_date.date()}'
        if beginner_class.class_type == 'beginner':
            d = {'beginner_class': beginner_class, 'minutes': 30}
        elif  beginner_class.class_type == 'returnee':
            d = {'beginner_class': beginner_class, 'minutes': 15}
        self.body = get_template('program_app/email/reminder_beginner.txt').render(d)
        self.attach_alternative(get_template('program_app/email/reminder_beginner.html').render(d), 'text/html')
        self.send()

    def status_email(self, class_list, staff):
        """Takes a list containing {'class': [beginner_class], 'instructors': [students], 'staff': [students]}"""
        self.bcc_from_users(staff)

        self.subject = f'WPA Class Status {class_list[0]["class"].class_date.date()}'
        logging.debug(class_list)

        self.body = get_template('program_app/email/status_email.txt').render({'class_list': class_list})
        self.attach_alternative(get_template('program_app/email/status_email.html').render({'class_list': class_list}),
                                'text/html')
        self.send()
