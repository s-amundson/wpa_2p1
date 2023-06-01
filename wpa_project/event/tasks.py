# Create your tasks here

from celery import shared_task
from django.db.models import Count

from django.utils import timezone
from django.conf import settings
from django.core.files.base import File

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame, Image, Spacer
from reportlab.lib.pagesizes import letter

from program_app.src import ClassRegistrationHelper, EmailMessage as ProgramEmailMessage
from student_app.src import EmailMessage
from program_app.tasks import update_waiting
from .models import Event, Registration
from payment.src import EmailMessage, RefundHelper

import os
from celery.utils.log import get_task_logger
import logging
logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)


@shared_task
def cancel_pending(reg_list, donated):
    registrations = Registration.objects.filter(pk__in=reg_list)

    # if an instructor cancels within 24 hours send an email to the instructors.
    staff_registrations = registrations.filter(
        student__user__is_staff=True,
        event__event_date__lt=timezone.now() + timezone.timedelta(hours=24),
        event__type='class'
    )
    if staff_registrations:
        for ir in staff_registrations.values('event').annotate(event_count=Count('event')).order_by():
            logger.warning(ir)
            celery_logger.warning(ir)
            logger.warning(type(ir['event']))
            reg = Registration.objects.filter(
                event__id=ir['event'],
                student__user__is_instructor=True,
                pay_status__in=['admin', 'paid']
            )
            celery_logger.warning(len(reg))
            # if there is less than 4 after we remove staff.
            if len(reg) < 4:
                celery_logger.warning('send instructors a warning')
                email_message = ProgramEmailMessage()
                email_message.instructor_canceled_email(ir['event'], len(reg))
    staff_registrations.update(pay_status='canceled')

    # remove the instructor registrations
    registrations = registrations.exclude(
        student__user__is_instructor=True,
        event__event_date__lt=timezone.now() + timezone.timedelta(hours=24),
        event__type='class'
    )

    # cancellations within 24 hours are not refundable
    not_refundable = registrations.filter(
        event__event_date__lt=timezone.now() + timezone.timedelta(hours=24),
        event__state__in=Event.event_states[:5]
    )
    not_refundable.update(pay_status='canceled')

    # remove the not_refundable
    registrations = registrations.exclude(
        event__event_date__lt=timezone.now() + timezone.timedelta(hours=24),
        event__state__in=Event.event_states[:5]
    )

    # volunteer events are not refundable
    volunteers = registrations.filter(event__type='work')
    volunteers.update(pay_status='canceled')
    registrations = registrations.exclude(event__type='work')

    # the remaining get refunded.
    refund = RefundHelper()
    for ikey in registrations.values('idempotency_key', 'pay_status').annotate(
            ik_count=Count('idempotency_key')).order_by():
        logging.warning(ikey)
        square_response = {'status': ''}
        icr = registrations.filter(idempotency_key=ikey['idempotency_key'])
        cost = icr[0].event.cost_standard
        # if ikey['pay_status'] in ['start', 'waiting']:
        #     icr.update(pay_status='canceled')
        #     continue
        if ikey['pay_status'] == 'cancel_pending' and donated:
            square_response = {'status': 'SUCCESS'}

        elif ikey['pay_status'] == 'cancel_pending':
            square_response = refund.refund_with_idempotency_key(ikey['idempotency_key'],
                                                                 cost * 100 * ikey['ik_count'])
        logger.warning(square_response)
        celery_logger.warning(square_response)
        if square_response['status'] in ['PENDING', 'SUCCESS']:
            if icr[0].user:
                EmailMessage().refund_email(icr[0].user, donated)
            else:  # since records are missing user.
                user = icr[0].student.student_family.student_set.filter(user__isnull=False).first().user
                EmailMessage().refund_email(user, donated)

            crh = ClassRegistrationHelper()
            for r in icr:
                if ikey['pay_status'] == 'cancel_pending':
                    if donated:
                        r.pay_status = 'refund donated'
                    else:
                        r.pay_status = 'refunded'
                else:
                    r.pay_status = 'canceled'
                r.save()
                crh.update_class_state(r.event.beginnerclass_set.last())
            update_waiting.delay(icr[0].event.beginnerclass_set.last().id)
        else:
            logger.warning('error')
            logger.warning(square_response['error'])
            # for r in icr:
            #     self.add_error(f'unreg_{r.id}', square_response['error'])
            # error_count += 1
        # reg = Registration.objects.filter(
        #     event=event,
        #     student__user__is_instructor=True,
        #     pay_status__in=['admin', 'paid']
        # )
        # celery_logger.warning(len(reg))
        # if len(reg) < 4:
        #     celery_logger.warning('send instructors a warning')
        #     email_message = ProgramEmailMessage()
        #     email_message.instructor_canceled_email(event, len(reg))
# if not len(cr):  # no registrations found
#     return True
# not_refundable = cr.filter(
#     event__event_date__lt=timezone.now() + timezone.timedelta(hours=24),
#     event__state__in=Event.event_states[:5]
# )
# logger.warning(not_refundable.update(pay_status='canceled'))
# if cr.filter(student__user__is_instructor=True,
#              event__event_date__lt=timezone.now() + timezone.timedelta(hours=24)):
#     # instructor canceled, check to see if we still have enough instructors.
#     instructor_canceled.delay(cr.last().event)
# cr = cr.filter(event__event_date__gte=timezone.now() + timezone.timedelta(hours=24),
#                event__state__in=Event.event_states[:4])
# logger.warning(cr)
#
# refund = RefundHelper()
# error_count = 0
# for ikey in cr.values('idempotency_key', 'pay_status').annotate(ik_count=Count('idempotency_key')).order_by():
#     logging.debug(ikey)
#     icr = cr.filter(idempotency_key=ikey['idempotency_key'])
#     cost = icr[0].event.cost_standard
#     if ikey['pay_status'] in ['start', 'waiting']:
#         icr.update(pay_status='canceled')
#         continue
#     elif ikey['pay_status'] == 'paid' and self.cleaned_data['donation']:
#         square_response = {'status': 'SUCCESS'}
#
#     elif ikey['pay_status'] == 'paid':
#         square_response = refund.refund_with_idempotency_key(ikey['idempotency_key'],
#                                                              cost * 100 * ikey['ik_count'])
#     logger.debug(square_response)
#
#     if square_response['status'] in ['PENDING', 'SUCCESS']:
#         if user.student_set.first().student_family == self.family:
#             EmailMessage().refund_email(user, self.cleaned_data['donation'])
#         else:
#             for s in self.family.student_set.all():
#                 if s.user is not None:
#                     EmailMessage().refund_email(s.user, self.cleaned_data['donation'])
#         crh = ClassRegistrationHelper()
#         for r in icr:
#             if ikey['pay_status'] == 'paid' and self.cleaned_data['donation']:
#                 r.pay_status = 'refund donated'
#             elif ikey['pay_status'] in ['paid', 'refunded']:
#                 r.pay_status = 'refunded'
#             else:
#                 r.pay_status = 'canceled'
#             r.save()
#             crh.update_class_state(r.event.beginnerclass_set.last())
#         update_waiting.delay(icr[0].event.beginnerclass_set.last().id)
#     else:
#         for r in icr:
#             self.add_error(f'unreg_{r.id}', square_response['error'])
#         error_count += 1
# return error_count == 0