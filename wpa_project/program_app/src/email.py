from django.template.loader import get_template
from django.utils import timezone

from student_app.src import EmailMessage
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMessage):
    def beginner_reminder(self, beginner_class, students):
        self.bcc_from_students(students)
        self.subject = f'WPA Class Reminder {timezone.localtime(beginner_class.event.event_date).date()}'
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

        self.subject = f'WPA Class Status {class_list[0]["class"].event.event_date.date()}'
        # logging.debug(class_list)

        self.body = get_template('program_app/email/status_email.txt').render({'class_list': class_list})
        self.attach_alternative(get_template('program_app/email/status_email.html').render({'class_list': class_list}),
                                'text/html')
        self.send()

    def wait_list_reminder(self, beginner_class, students):
        self.bcc_from_students(students)
        self.subject = f'WPA Class Wait List Reminder {timezone.localtime(beginner_class.event.event_date).date()}'
        if beginner_class.class_type == 'beginner':
            d = {'beginner_class': beginner_class, 'minutes': 30}
        elif beginner_class.class_type == 'returnee':
            d = {'beginner_class': beginner_class, 'minutes': 15}
        self.body = get_template('program_app/email/reminder_wait.txt').render(d)
        self.attach_alternative(get_template('program_app/email/reminder_wait.html').render(d), 'text/html')
        self.send()

    def wait_list_off(self, registrations):
        """Send mail students that they have been removed from wait list and their card charged."""
        beginner_class = registrations[0].beginner_class
        self.get_email_address(registrations[0].user)
        if beginner_class.class_type == 'beginner':
            d = {'beginner_class': beginner_class, 'minutes': 30}
        elif  beginner_class.class_type == 'returnee':
            d = {'beginner_class': beginner_class, 'minutes': 15}
        line_items = []

        for r in registrations:
            line_items.append({
                'name': f'Class on {str(r.beginner_class.event.event_date)[:10]} student: {r.student.first_name}',
                'quantity': 1,
                'amount_each': r.beginner_class.event.cost_standard,
                'cost': r.beginner_class.event.cost_standard})
        d['line_items'] = line_items
        d['total'] = beginner_class.event.cost_standard * len(registrations)
        self.subject = f'WPA class registration status change for class on {beginner_class.event.event_date.date()}'
        self.body = get_template('program_app/email/wait_list_off.txt').render(d)
        self.attach_alternative(get_template('program_app/email/wait_list_off.html').render(d),
                                'text/html')
        self.send()
