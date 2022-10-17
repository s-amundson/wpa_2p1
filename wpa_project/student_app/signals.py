import logging

from django.dispatch import receiver
from allauth.account.signals import email_changed, email_confirmed, user_signed_up
from ipware import get_client_ip
from .models import Student, User
from contact_us.models import Email

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


@receiver(user_signed_up)
def user_signed_up(request, user, **kwargs):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        logging.warning(f'unable to get ip for {user.email}')
    else:
        try:
            e = Email.objects.get(email=user.email)
            e.ip = client_ip
            e.save()
        except Email.DoesNotExist:
            logging.warning(f'email for user {user.id} does not exist')

    logging.warning(get_client_ip(request))
