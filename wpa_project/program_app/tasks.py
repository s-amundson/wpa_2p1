# Create your tasks here
from celery import shared_task
from django.utils import timezone

from .src import ClassRegistrationHelper
from .models import BeginnerClass, ClassRegistration
from payment.src import EmailMessage, RefundHelper

import logging
logger = logging.getLogger(__name__)
crh = ClassRegistrationHelper()


@shared_task
def charge_group(reg_list):
    crh.charge_group(ClassRegistration.objects.filter(id__in=reg_list))


@shared_task
def refund_class(beginner_class):
    if type(beginner_class) == int:
        beginner_class = BeginnerClass.objects.get(pk=beginner_class)
    ec = ClassRegistrationHelper().enrolled_count(beginner_class)
    refund = RefundHelper()
    email_message = EmailMessage()
    # need to refund students if any
    if ec["beginner"] > 0 or ec["returnee"] > 0:
        cr = ClassRegistration.objects.filter(beginner_class__id=beginner_class.id)
        ik_list = []
        for reg in cr:
            if reg.idempotency_key not in ik_list:
                ik_list.append(reg.idempotency_key)
                qty = len(cr.filter(idempotency_key=reg.idempotency_key).filter(pay_status='paid'))
                square_response = refund.refund_with_idempotency_key(reg.idempotency_key, qty * beginner_class.cost * 100)
                if square_response['status'] == 'error':
                    if square_response['error'] != 'Previously refunded':  # pragma: no cover
                        logging.error(square_response)
                else:
                    email_sent = False
                    for c in cr.filter(idempotency_key=reg.idempotency_key):
                        c.pay_status = 'refund'
                        c.save()
                        if c.student.user is not None:
                            email_message.refund_canceled_email(
                                c.student.user, f'Class on {str(timezone.localtime(beginner_class.class_date))[:10]}')
                            email_sent = True
                    if not email_sent:  # if none of the students is a user find a user in the family.
                        c = cr.filter(idempotency_key=reg.idempotency_key)[0]
                        for s in c.student.student_family.student_set.all():
                            if s.user is not None:
                                email_message.refund_canceled_email(
                                    s.user, f'Class on {str(timezone.localtime(beginner_class.class_date))[:10]}')


@shared_task
def update_waiting(beginner_class):
    crh.update_waiting(beginner_class)
