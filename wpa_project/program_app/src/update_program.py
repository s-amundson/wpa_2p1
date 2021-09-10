import logging
from django.utils import timezone
from datetime import timedelta

from ..models import BeginnerClass

logger = logging.getLogger(__name__)


class UpdatePrograms:
    def beginner_class(self):
        states = BeginnerClass().get_states()

        # close tomorrows class
        d = timezone.localtime(timezone.now()).date() + timedelta(days=2)
        classes = BeginnerClass.objects.filter(class_date__lte=d, state__in=states[:3])
        for c in classes:
            c.state = states[3]  # 'closed'
            c.save()

        # # open next weeks class
        # d = date.today() + timedelta(days=6)
        # bc = m.objects.filter(class_date__lte=d, state=states[0])
        # bc.state = states[1]  # 'open'

        # create class day after tomorrow and open
        d = timezone.localtime(timezone.now()).date() + timedelta(days=2)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        bc = BeginnerClass(class_date=d, beginner_limit=10, returnee_limit=10, state='open')
        bc.save()
