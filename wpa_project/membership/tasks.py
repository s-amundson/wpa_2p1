import logging
from django.utils import timezone
from datetime import timedelta
from celery import shared_task

from membership.models import Member
from membership.src import EmailMessage
# logger = logging.getLogger(__name__)
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task
def membership_expire():
    # Update the memberships that have expired.
    d = timezone.localtime(timezone.now()).date()
    expired_members = Member.objects.filter(expire_date__lt=d)
    for member in expired_members:
        u = member.student.user
        logging.debug(u.id)
        u.is_member = False
        u.save()

    logger.warning(d + timedelta(days=14))
    print(d + timedelta(days=14))
    # Send notifications to members that are about to expire
    notice_members = Member.objects.filter(expire_date=d + timedelta(days=14))
    logger.warning(notice_members)
    print(notice_members)
    em = EmailMessage()
    for member in notice_members:
        # em.expire_notice(member)
        pass

