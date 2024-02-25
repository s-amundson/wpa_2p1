import logging

from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Member, Membership
from payment.models import PaymentLog
from payment.signals import payment_error_signal
from src.years import add_years

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentLog)
def member_update(sender, instance, created, **kwargs):
    memberships = Membership.objects.filter(idempotency_key=instance.idempotency_key)
    if instance.status in ["SUCCESS", 'COMPLETED', 'volunteer points', 'comped']:
        for membership in memberships:
            membership.pay_status = 'paid'
            for student in membership.students.all():
                member, created = Member.objects.update_or_create(student=student)
                member.level = membership.level
                try:
                    member.expire_date = member.expire_date.date()
                except AttributeError:
                    pass
                if member.expire_date > timezone.datetime.now().date():
                    member.expire_date = add_years(member.expire_date, 1)
                else:
                    member.expire_date = add_years(timezone.datetime.today(), 1)
                    member.begin_date = timezone.datetime.today()
                logging.debug(member.expire_date)
                member.save()

                # set is_member in user
                if student.user is not None:
                    student.user.is_member = True
                    student.user.save()
            membership.save()


@receiver(payment_error_signal)
def payment_error(old_idempotency_key, new_idempotency_key, **kwargs):
    """ in case of a payment error update the registration with the new idempotency key so that we register them once
    a successful payment is processed"""
    m = Membership.objects.filter(idempotency_key=old_idempotency_key)
    m.update(idempotency_key=new_idempotency_key)
