import logging

from django.dispatch import receiver
from allauth.account.signals import email_changed, email_confirmed, user_logged_in, user_signed_up
from .models import Student, User

logger = logging.getLogger(__name__)


@receiver(email_changed)
def email_update(request, user, from_email_address, to_email_address, **kwargs):
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

@receiver(user_logged_in)
def user_logged_in(request, user, **kwargs):
    request.session['theme'] = user.theme

