# Create your tasks here
from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.conf import settings

from .src import ClassRegistrationHelper, UpdatePrograms
from .models import BeginnerClass, BeginnerSchedule, ClassRegistration
from payment.src import EmailMessage, RefundHelper

import logging
logger = logging.getLogger(__name__)
crh = ClassRegistrationHelper()


# @shared_task
# def add_classes(day_of_week=timezone.now().weekday()):
#     logging.warning(day_of_week)
#     classes = BeginnerSchedule.objects.filter(day_of_week=day_of_week)

@shared_task
def charge_group(reg_list):  # pragma: no cover
    crh.charge_group(ClassRegistration.objects.filter(id__in=reg_list))


@shared_task
def close_create_class(schedule_id):
    beginner_schedule = BeginnerSchedule.objects.get(pk=schedule_id)
    update_programs = UpdatePrograms()
    update_programs.close_class(beginner_schedule.class_time)
    update_programs.create_class(beginner_schedule)


@shared_task
def daily_update():
    update_programs = UpdatePrograms()
    update_programs.record_classes()
    update_programs.status_email()


@shared_task
def init_class():
    UpdatePrograms().add_weekly()
    for c in BeginnerSchedule.objects.all():
        # Schedule the reminder email 2 days prior to the event.
        if c.day_of_week - 2 >= 0:
            day_of_week = c.day_of_week - 2
        else:
            day_of_week = c.day_of_week + 7 - 2
        reminder_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=f'{c.class_time.minute}',
            hour=f'{c.class_time.hour}',
            day_of_week=f'{day_of_week}',
            day_of_month='*',
            month_of_year='*',
            timezone=settings.TIME_ZONE
        )
        PeriodicTask.objects.update_or_create(
            crontab=reminder_schedule,
            name=f'Beginner Schedule {c.id} reminder email',
            task='program_app.tasks.reminder_email',
            description='send reminder email to students',
            enabled=True,
            args=[c.id],
            defaults={'name': f'Beginner Schedule {c.id} reminder email'}
        )

        # Schedule close the class 1 day before event
        if c.day_of_week - 1 >= 0:
            day_of_week = c.day_of_week - 1
        else:
            day_of_week = c.day_of_week + 7 - 1
        close_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=f'{c.class_time.minute}',
            hour=f'{c.class_time.hour}',
            day_of_week=f'{day_of_week}',
            day_of_month='*',
            month_of_year='*',
            timezone=settings.TIME_ZONE
        )
        PeriodicTask.objects.update_or_create(
            crontab=close_schedule,
            name=f'Beginner Schedule {c.id} close create class',
            task='program_app.tasks.close_create_class',
            description='close the class and create an new one',
            enabled=True,
            args=[c.id],
            defaults={'name': f'Beginner Schedule {c.id} close create class'}
        )


@shared_task
def refund_class(beginner_class, message=''):
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
                square_response = refund.refund_with_idempotency_key(
                    reg.idempotency_key, qty * beginner_class.cost * 100)
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
                                c.student.user,
                                f'Class on {str(timezone.localtime(beginner_class.class_date))[:10]}',
                                message
                            )
                            email_sent = True
                    if not email_sent:  # if none of the students is a user find a user in the family.
                        c = cr.filter(idempotency_key=reg.idempotency_key)[0]
                        for s in c.student.student_family.student_set.all():
                            if s.user is not None:
                                email_message.refund_canceled_email(
                                    s.user,
                                    f'Class on {str(timezone.localtime(beginner_class.class_date))[:10]}',
                                    message
                                )


@shared_task
def reminder_email(schedule_id):
    beginner_schedule = BeginnerSchedule.objects.get(pk=schedule_id)
    update_programs = UpdatePrograms()
    update_programs.reminder_email(beginner_schedule.class_time)


@shared_task
def update_waiting(beginner_class):
    crh.update_waiting(beginner_class)
