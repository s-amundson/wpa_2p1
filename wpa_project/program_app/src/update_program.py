import logging
from django.utils import timezone
from datetime import timedelta

from ..models import BeginnerClass, ClassRegistration
from ..src import ClassRegistrationHelper, EmailMessage
from student_app.models import Student, User

logger = logging.getLogger(__name__)


class UpdatePrograms:
    def beginner_class(self):
        crh = ClassRegistrationHelper()
        states = BeginnerClass().get_states()
        today = timezone.localtime(timezone.now()).date()

        # send status update for classes 3 days from now.
        email_date = today + timedelta(days=3)
        logging.debug(email_date)
        staff_query = User.objects.filter(is_staff=True, is_active=True)
        students = Student.objects.filter(user__in=staff_query)
        classes = BeginnerClass.objects.filter(class_date__date=email_date, state__in=states[:3])
        logging.debug(len(classes))
        if len(classes):
            class_list = []
            for c in classes:
                instructors = []
                staff = []
                cr = ClassRegistration.objects.filter(beginner_class=c, student__in=students)
                for r in cr:
                    if r.student.user.is_instructor:
                        instructors.append(r.student)
                    else:
                        staff.append(r.student)
                class_list.append({'class': c, 'instructors': instructors, 'staff': staff,
                                   'count': crh.enrolled_count(c)})
            logging.debug(class_list)
            EmailMessage().status_email(class_list, staff_query)
            logging.debug('emailed')

        # set past classes to recorded
        yesterday = today - timedelta(days=1)
        classes = BeginnerClass.objects.filter(class_date__lte=yesterday, state__in=states[:4])
        logging.debug(len(classes))
        for c in classes:
            c.state = states[5]  # 'recorded'
            c.save()

        # close tomorrow's class
        tomorrow = today + timedelta(days=1)
        tomorrow = timezone.datetime.combine(tomorrow, timezone.datetime.max.time())
        classes = BeginnerClass.objects.filter(class_date__lte=tomorrow, state__in=states[:3])
        for c in classes:
            c.state = states[3]  # 'closed'
            c.save()
            logging.debug(c.state)

        # create classes for the next month on saturday if doesn't exist
        next_sat = self.next_class_day(5)  # Monday is 0 and Sunday is 6

        for i in range(4):
            class_day = next_sat + timedelta(days=(7*i))
            class_day = timezone.datetime.combine(class_day, timezone.datetime.min.time())
            class_day = class_day.replace(hour=9)
            classes = BeginnerClass.objects.filter(class_date=class_day)
            if len(classes) == 0:
                bc = BeginnerClass(class_date=class_day, class_type='beginner', beginner_limit=35, returnee_limit=0,
                                   state='open')
                bc.save()
            class_day = class_day.replace(hour=11)
            classes = BeginnerClass.objects.filter(class_date=class_day)
            if len(classes) == 0:
                bc = BeginnerClass(class_date=class_day, class_type='returnee', beginner_limit=0, returnee_limit=35,
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
