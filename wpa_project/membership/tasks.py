import logging
import traceback
from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from django_celery_beat.models import PeriodicTask
from django.contrib.auth.models import Group

from membership.models import Election, Member, Membership
from membership.src import EmailMessage
from payment.models import PaymentLog
from .signals import member_update
logger = logging.getLogger('membership')
from celery.utils.log import get_task_logger
celery_logger = get_task_logger(__name__)


@shared_task(bind=True, ignore_result=True)
def debug_task(self):  # pragma: no cover
    celery_logger.debug('membership debug task')
    celery_logger.warning('membership debug task')
    logger.warning('membership debug task')


@shared_task
def membership_election_close(election_id):
    election = Election.objects.get(pk=election_id)
    election.state = 'closed'
    election.save()
    em = EmailMessage()
    em.election_result(election)


def membership_election_calendar_notify(last_run):
    """ Send out a notification about election 7 days before election."""
    election_notification_days = [2, 7]
    em = EmailMessage()
    for nd in election_notification_days:
        elections = Election.objects.filter(election_date__lte=timezone.now() + timedelta(days=nd))
        if last_run is not None:
            elections = elections.filter(election_date__gte=last_run + timedelta(days=nd))
        logger.warning(elections)
        for election in elections:
            em.election_notification(election)


@shared_task
def membership_expire_notice():
    celery_logger.warning('membership membership expire notice')

    d = timezone.localtime(timezone.now()).date()
    logger.warning(d + timedelta(days=14))
    # Send notifications to members that are about to expire
    notice_members = Member.objects.filter(expire_date__in=[d + timedelta(days=7), d + timedelta(days=14)])
    logger.critical(notice_members)
    celery_logger.critical(notice_members)
    em = EmailMessage()
    for member in notice_members:
        em.expire_notice(member)


@shared_task
def membership_expire_update():
    logger.warning('membership membership expire update')
    # Update the memberships that have expired.
    d = timezone.localtime(timezone.now()).date()
    try:
        expired_members = Member.objects.filter(expire_date__lt=d)
        logger.warning(expired_members)
        for member in expired_members:
            u = member.student.user
            if u is not None:
                u.groups.remove(Group.objects.get(name='members'))
    except Exception as e:  # pragma: no cover
        logger.error(traceback.format_exc())
        # Logs the error appropriately.


def membership_user_update():
    # occasionally the signal is missed so check the membership payments and
    memberships = Membership.objects.filter(pay_status='start')
    logger.warning(memberships)
    for m in memberships:
        pl = PaymentLog.objects.get(idempotency_key=m.idempotency_key)
        member_update(None, pl, False)