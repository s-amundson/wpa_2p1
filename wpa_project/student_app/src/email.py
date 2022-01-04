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
