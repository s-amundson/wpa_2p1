# Create your tasks here

from celery import shared_task
from django.db.models import Count

from django.utils import timezone


from program_app.src import ClassRegistrationHelper, EmailMessage as ProgramEmailMessage
from student_app.src import EmailMessage
from program_app.tasks import update_waiting
from .models import Event, Registration
from payment.src import EmailMessage, RefundHelper

from celery.utils.log import get_task_logger
import logging
logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)


@shared_task
def cancel_event(event, cancel_message=""):
    if type(event) == int:
        event = Event.objects.get(pk=event)
    email_message = EmailMessage()
    event_type = 'event'
    if event.beginnerclass_set.count():
        event_type = 'class'
    elif event.volunteerevent_set.count():
        event_type = 'volunteer event'
    registrations = event.registration_set.filter(pay_status__in=['admin', 'comped', 'paid'])
    ik_list = []
    for reg in registrations:
        if reg.idempotency_key not in ik_list:
            ik_list.append(reg.idempotency_key)
            email_sent = False
            transaction = registrations.filter(idempotency_key=reg.idempotency_key)

            for c in transaction:
                if c.student.user is not None:
                    email_message.event_canceled_email(
                        c.student.user,
                        f'{event_type} on {str(timezone.localtime(event.event_date))[:10]}',
                        cancel_message, False
                    )
                    email_sent = True
                    transaction.update(pay_status='canceled')
            if not email_sent:  # if none of the students is a user find a user in the family.
                c = transaction.first()
                if c:
                    for s in c.student.student_family.student_set.all():
                        if s.user is not None:
                            email_message.event_canceled_email(
                                s.user,
                                f'{event_type} on {str(timezone.localtime(event.event_date))[:10]}',
                                cancel_message, False
                            )
                            transaction.update(pay_status='canceled')


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
                email_message.instructor_canceled_email(Event.objects.get(pk=ir['event']), len(reg))
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
