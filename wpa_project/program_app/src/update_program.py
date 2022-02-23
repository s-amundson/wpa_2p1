import logging
from django.utils import timezone
from datetime import timedelta

from ..models import BeginnerClass

logger = logging.getLogger(__name__)


class UpdatePrograms:
    def beginner_class(self):
        states = BeginnerClass().get_states()

        # close tomorrow's class
        tomorrow = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        tomorrow = timezone.datetime.combine(tomorrow, timezone.datetime.max.time())
        logging.debug(tomorrow)
        classes = BeginnerClass.objects.filter(class_date__lte=tomorrow, state__in=states[:3])
        logging.debug(len(classes))
        for c in classes:
            c.state = states[3]  # 'closed'
            c.save()
            logging.debug(c.state)

        # create classes for the next month on saturday if doesn't exist
        next_sat = self.next_class_day(5)  # Monday is 0 and Sunday is 6
        classes = BeginnerClass.objects.filter(class_date__gt=tomorrow)

        for i in range(4):
            class_day = next_sat + timedelta(days=(7*i))
            class_day = timezone.datetime.combine(class_day, timezone.datetime.min.time())
            class_day = class_day.replace(hour=9)
            logging.debug(class_day)
            classes = BeginnerClass.objects.filter(class_date=class_day)
            if len(classes) == 0:
                bc = BeginnerClass(class_date=class_day, class_type='beginner', beginner_limit=30, returnee_limit=0,
                                   state='open')
                bc.save()
            class_day = class_day.replace(hour=11)
            classes = BeginnerClass.objects.filter(class_date=class_day)
            if len(classes) == 0:
                bc = BeginnerClass(class_date=class_day, class_type='returnee', beginner_limit=0, returnee_limit=30,
                                   state='open')
                bc.save()

    def next_class_day(self, target_day):
        """Returns the next eligible class day (not today or tomorrow)
        target_day is  0-6. Monday is 0 and Sunday is 6"""
        target_day = target_day % 7
        today = timezone.localtime(timezone.now()).date()
        target_delta = target_day - today.weekday()
        while target_delta <= 1:
            target_delta += 7
        return today + timedelta(target_delta)
