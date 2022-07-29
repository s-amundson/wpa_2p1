import logging

from django.utils import timezone, datetime_safe
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Member, Membership
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
    except ValueError:  # pragma: no cover
        return d + (datetime_safe.date(d.year + years, 1, 1) - datetime_safe.date(d.year, 1, 1))


@receiver(post_save, sender=PaymentLog)
def member_update(sender, instance, created, **kwargs):
    memberships = Membership.objects.filter(idempotency_key=instance.idempotency_key)
    if instance.status in ["SUCCESS", 'COMPLETED']:
        for membership in memberships:
            membership.pay_status = 'paid'
            for student in membership.students.all():
                member, created = Member.objects.update_or_create(student=student)
                member.level = membership.level
                try:
                    member.expire_date = member.expire_date.date()
                except AttributeError:
                    pass
                if member.expire_date > datetime_safe.date.today():
                    member.expire_date = add_years(member.expire_date, 1)
                else:
                    member.expire_date = add_years(datetime_safe.date.today(), 1)
                    member.begin_date = datetime_safe.date.today()
                logging.debug(member.expire_date)
                member.save()

                # set is_member in user
                if student.user is not None:
                    student.user.is_member = True
                    student.user.save()
            membership.save()
    #
    # if created:
    #     pass
    # #     MembershipModel.objects.create(user=instance)
