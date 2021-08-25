import logging

from django.utils import timezone, datetime_safe
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import MemberModel, MembershipModel
from payment.models import PaymentLog

logger = logging.getLogger(__name__)


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (datetime_safe.date(d.year + years, 1, 1) - datetime_safe.date(d.year, 1, 1))


@receiver(post_save, sender=PaymentLog)
def member_update(sender, instance, created, **kwargs):
    if instance.db_model == 'Membership':
        membership = MembershipModel.objects.get(idempotency_key=instance.idempotency_key)
        logging.debug(instance.status)
        if instance.status == "SUCCESS":
            membership.pay_status = 'paid'
            for student in membership.students.all():
                member, created = MemberModel.objects.update_or_create(student=student)
                member.level = membership.level
                try:
                    member.expire_date = member.expire_date.date()
                except AttributeError:
                    pass
                if member.expire_date > datetime_safe.date.today():
                    member.expire_date = add_years(member.expire_date, 1)
                else:
                    member.expire_date = add_years(datetime_safe.date.today(), 1)
                logging.debug(member.expire_date)
                member.save()
        else:
            membership.pay_status = 'error'

    if created:
        pass
    #     MembershipModel.objects.create(user=instance)
