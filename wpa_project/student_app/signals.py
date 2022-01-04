import logging

from django.dispatch import receiver
from allauth.account.signals import email_changed, email_confirmed
from .models import Student, User

logger = logging.getLogger(__name__)


@receiver(email_changed)
def email_update(request, user, from_email_address, to_email_address, **kwargs):
    logging.debug(to_email_address.email)
    try:
        student = Student.objects.get(user=user)
        student.email = to_email_address.email
        student.save()
    except Student.DoesNotExist:  # pragma: no cover
        pass


@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    try:
        student = Student.objects.get(email=email_address.email)

    except Student.DoesNotExist:  # pragma: no cover
        student = None
    if student is not None:
        if student.user is None:
            user = User.objects.get(email=email_address.email)
            student.user = user
            student.save()
            logging.debug('added user to student')
