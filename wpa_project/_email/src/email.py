from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone
import logging

from _email.models import BulkEmail, EmailCounts

logger = logging.getLogger(__name__)


class EmailMessage(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.html = ""
        self.test_emails = ["EmilyNConlan@einrot.com", "RosalvaAHall@superrito.com", "CharlesNWells@einrot.com",
                            "RicardoRHoyt@jourrapide.com", "RicardoRHoyt@Ricardo.com"]

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

    def send(self, fail_silently=False):
        counts, created = EmailCounts.objects.get_or_create(date=timezone.datetime.today())
        counts.to += len(self.to)
        counts.cc += len(self.cc)
        counts.bcc += len(self.bcc)
        counts.save()
        super().send(fail_silently)

    def paragraph_message(self, message):
        paragraphs = []
        for line in message.split('\n'):
            if len(line) > 1:
                paragraphs.append(line)
        return paragraphs

    def send_mass_bcc(self, users, subject, body, html, priority=0, fail_silently=False):
        """Add email to a que to email out to users."""
        for i in range(0, len(users), settings.EMAIL_BCC_LIMIT):
            if len(users) - i > settings.EMAIL_BCC_LIMIT:
                bcc = users[i: i + settings.EMAIL_BCC_LIMIT]
            else:
                bcc = users[i:]
            # logger.warning(bcc)
            bulk_email = BulkEmail.objects.create(subject=subject, body=body, html=html)
            bulk_email.users.add(*bcc)

    def send_mass_message(self, users, subject, message):
        d = {'name': '', 'paragraphs': self.paragraph_message(message)}
        self.send_mass_bcc(users,
                           subject,
                           get_template('email/paragraph_message.txt').render(d),
                           get_template('email/paragraph_message.html').render(d))

    def send_message(self, subject, message):
        self.subject = subject

        d = {'name': '', 'paragraphs': self.paragraph_message(message)}
        self.body = get_template('email/paragraph_message.txt').render(d)
        self.attach_alternative(get_template('email/paragraph_message.html').render(d), 'text/html')
        send_list = self.bcc
        for i in range(0, len(send_list), settings.EMAIL_BCC_LIMIT):
            if len(send_list) - i > settings.EMAIL_BCC_LIMIT:
                self.bcc = send_list[i: i + settings.EMAIL_BCC_LIMIT]
            else:
                self.bcc = send_list[i: len(send_list)]
            self.send()

    def invite_user_email(self, send_student, add_student):
        self.to = [add_student.email]
        d = {'add_name': add_student.first_name, 'send_name': send_student.first_name}
        self.subject = 'Woodley Park Archers Invitation'
        self.body = get_template('email/invite_email.txt').render(d)
        self.attach_alternative(get_template('email/invite_email.html').render(d), 'text/html')
        self.send()
