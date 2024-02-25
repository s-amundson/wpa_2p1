from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.test_emails = ["EmilyNConlan@einrot.com", "RosalvaAHall@superrito.com", "CharlesNWells@einrot.com",
                            "RicardoRHoyt@jourrapide.com", "RicardoRHoyt@Ricardo.com"]

    def awrl_email(self, student):
        if not student.signature_pdf:
            logging.warning("No signature to send")
            return
        if student.user is not None:
            self.get_email_address(student.user)
            name = f'{student.first_name} {student.last_name}'
        else:
            students = student.student_family.student_set.all().order_by('id')
            for s in students:
                # logging.debug(f'id: {s.id}, user: {s.user}')
                if s.user is not None:
                    self.get_email_address(s.user)
                    name = f'{s.first_name} {s.last_name}'
                    break
        self.subject = "Woodley Park Archers AWRL agreement"
        student_name = f'{student.first_name} {student.last_name}'
        d = {'name': name,
             'message': f'Attached is the Accident Waiver and Release of Liability for {student_name}'}
        self.body = get_template('student_app/email/simple_message.txt').render(d)
        self.attach_alternative(get_template('student_app/email/simple_message.html').render(d), 'text/html')
        self.attach(f'{student_name}.pdf', student.signature_pdf.read())
        self.send()

    def bcc_append(self, address):
        if address.verified and address not in self.bcc:
            self.bcc.append(address)

    def bcc_append_user(self, user):
        if user.is_active:
            self.bcc_append(EmailAddress.objects.get_primary(user))

    def bcc_from_students(self, queryset, append=False):
        if not append:
            self.bcc = []

        for row in queryset:
            if row.user is not None:
                self.bcc_append_user(row.user)
            else:
                family = row.student_family.student_set.filter(user__isnull=False)
                for s in family:
                    self.bcc_append_user(s.user)

    def bcc_from_users(self, users, append=False):
        if not append:
            self.bcc = []

        for user in users:
            self.bcc_append_user(user)

    def get_email_address(self, user):
        if settings.EMAIL_DEBUG:  # pragma: no cover
            self.to = settings.EMAIL_DEBUG_ADDRESSES
        else:
            self.to = [EmailAddress.objects.get_primary(user)]
            if self.to in self.test_emails:
                self.to = settings.EMAIL_DEBUG_ADDRESSES

    def send_message(self, subject, message):
        self.subject = subject
        paragraphs = []
        for line in message.split('\n'):
            if len(line) > 1:
                paragraphs.append(line)
        d = {'name': '', 'paragraphs': paragraphs}
        self.body = get_template('student_app/email/paragraph_message.txt').render(d)
        self.attach_alternative(get_template('student_app/email/paragraph_message.html').render(d), 'text/html')
        self.send()

    def invite_user_email(self, send_student, add_student):
        self.to = [add_student.email]
        d = {'add_name': add_student.first_name, 'send_name': send_student.first_name}
        self.subject = 'Woodley Park Archers Invitation'
        self.body = get_template('student_app/email/invite_email.txt').render(d)
        self.attach_alternative(get_template('student_app/email/invite_email.html').render(d), 'text/html')
        self.send()
