import logging
from django.utils import timezone
from datetime import timedelta

from ..models import Member
from ..src import EmailMessage
logger = logging.getLogger(__name__)


class RunDaily:
    def expire(self):
        # Update the memberships that have expired.
        d = timezone.localtime(timezone.now()).date()
        expired_members = Member.objects.filter(expire_date__lt=d)
        for member in expired_members:
            u = member.student.user
            logging.debug(u.id)
            u.is_member = False
            u.save()

        # Send notifications to members that are about to expire
        logging.debug(d - timedelta(days=14))
        notice_members = Member.objects.filter(expire_date=d + timedelta(days=14))
        em = EmailMessage()
        for member in notice_members:
            em.expire_notice(member)


