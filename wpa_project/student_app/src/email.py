from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

# from wpa_project.student_app.models import ClassRegistration
import logging

logger = logging.getLogger(__name__)


class EmailMessage(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.test_emails = ["EmilyNConlan@einrot.com", "RosalvaAHall@superrito.com", "CharlesNWells@einrot.com",
                            "RicardoRHoyt@jourrapide.com", "RicardoRHoyt@Ricardo.com"]

    def awrl_email(self, student):
        if student.signature_pdf is None:
            logging.warning("No signature to send")
            return
        if student.user is not None:
            self.get_email_address(student.user)
            name = f'{student.first_name} {student.last_name}'
        else:
            students = student.student_family.student_set.all().order_by('id')
            for s in students:
                logging.debug(f'id: {s.id}, user: {s.user}')
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

    def bcc_from_students(self, queryset):
        self.bcc = []
        for row in queryset:
            if row.user is not None:
                self.bcc.append(EmailAddress.objects.get_primary(row.user))
        logging.debug(self.bcc)

    def get_email_address(self, user):
        if settings.EMAIL_DEBUG:
            self.to = settings.EMAIL_DEBUG_ADDRESSES
        else:  # pragma: no cover
            self.to = [EmailAddress.objects.get_primary(user)]
            if self.to in self.test_emails:
                self.to = settings.EMAIL_DEBUG_ADDRESSES

    def invite_user_email(self, send_student, add_student):
        logging.debug(add_student.email)
        self.to = [add_student.email]
        d = {'add_name': add_student.first_name, 'send_name': send_student.first_name}
        self.subject = 'Woodley Park Archers Invitation'
        self.body = get_template('student_app/email/invite_email.txt').render(d)
        self.attach_alternative(get_template('student_app/email/invite_email.html').render(d), 'text/html')
        self.send()
