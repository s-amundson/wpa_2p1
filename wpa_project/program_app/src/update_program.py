import logging
from django.utils import timezone
from datetime import timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from ..models import BeginnerClass, BeginnerSchedule, ClassRegistration
from ..src import ClassRegistrationHelper, EmailMessage
from student_app.models import Student, User

logger = logging.getLogger(__name__)


def close_class_job(class_time):
    UpdatePrograms().close_class(class_time)


def reminder_email_job(class_time):
    UpdatePrograms().reminder_email(class_time)


class SchedulePrograms:
    def __init__(self, scheduler):
        self.scheduler = scheduler

        scheduled_classes = BeginnerSchedule.objects.all()
        for c in scheduled_classes:
            self.scheduler.add_job(
                reminder_email_job,
                trigger=CronTrigger(day_of_week=c.day_of_week - 2,
                                    hour=c.class_time.hour,
                                    minute=c.class_time.minute),
                id=f'reminder_email_{c.id}',  # The `id` assigned to each job MUST be unique
                max_instances=1,
                replace_existing=True,
                kwargs={'class_time': c.class_time}
            )
            self.scheduler.add_job(
                close_class_job,
                trigger=CronTrigger(day_of_week=c.day_of_week - 1,
                                    hour=c.class_time.hour,
                                    minute=c.class_time.minute),
                id=f'close_{c.id}',  # The `id` assigned to each job MUST be unique
                max_instances=1,
                replace_existing=True,
                kwargs={'class_time': c.class_time}
            )


class UpdatePrograms:
    def __init__(self):
        self.email = EmailMessage()
        self.states = BeginnerClass().get_states()
        self.today = timezone.localtime(timezone.now()).date()

    def add_weekly(self):
        scheduled_classes = BeginnerSchedule.objects.all()
        for c in scheduled_classes:
            next_class = self.next_class_day(c.day_of_week)
            for i in range(c.future_classes):
                class_day = next_class + timedelta(days=(7 * i))
                class_day = timezone.datetime.combine(class_day, c.class_time)
                class_day = timezone.make_aware(class_day, timezone.get_current_timezone())
                classes = BeginnerClass.objects.filter(class_date=class_day)
                if len(classes) == 0:
                    bc = BeginnerClass(
                        class_date=class_day,
                        class_type=c.class_type,
                        beginner_limit=c.beginner_limit,
                        returnee_limit=c.returnee_limit,
                        state=c.state)
                    bc.save()

    def close_class(self, class_time):
        class_date = timezone.datetime.combine(self.today + timedelta(days=1), class_time)
        classes = BeginnerClass.objects.filter(class_date=class_date, state__in=self.states[:3])
        for c in classes:
            c.state = self.states[3]  # 'closed'
            c.save()
            logging.debug(c.state)

    def daily_update(self):
        self.add_weekly()
        self.status_email()

        # set past classes to recorded
        yesterday = self.today - timedelta(days=1)
        classes = BeginnerClass.objects.filter(class_date__lte=yesterday, state__in=self.states[:4])
        logging.debug(len(classes))
        for c in classes:
            c.state = self.states[5]  # 'recorded'
            c.save()

    def next_class_day(self, target_day):
        """Returns the next eligible class day (not today or tomorrow)
        target_day is  0-6. Monday is 0 and Sunday is 6"""
        target_day = target_day % 7
        target_delta = target_day - self.today.weekday()
        while target_delta <= 1:
            target_delta += 7
        return self.today + timedelta(target_delta)

    def reminder_email(self, class_time):
        # send reminder email to students for classes 2 days from now.
        staff_query = User.objects.filter(is_staff=True, is_active=True)
        class_date = timezone.datetime.combine(self.today + timedelta(days=2), class_time)
        classes = BeginnerClass.objects.filter(class_date=class_date, state__in=self.states[:3])
        logging.debug(classes)
        for c in classes:
            cr = c.classregistration_set.filter(pay_status__in=['paid', 'admin'])  #.exclude(student__in=staff_students)
            logging.debug(cr)
            logging.debug(c)
            student_list = []
            for r in cr:
                student_list.append(r.student.id)
            students = Student.objects.filter(id__in=student_list)
            students = students.exclude(user__in=staff_query)
            logging.debug(students)
            self.email.beginner_reminder(c, students)

    def status_email(self):
        crh = ClassRegistrationHelper()
        email_date = self.today + timedelta(days=3)
        logging.debug(email_date)
        staff_query = User.objects.filter(is_staff=True, is_active=True)
        staff_students = Student.objects.filter(user__in=staff_query)
        classes = BeginnerClass.objects.filter(class_date__date=email_date, state__in=self.states[:3])
        logging.debug(len(classes))
        if len(classes):
            class_list = []
            for c in classes:
                instructors = []
                staff = []
                cr = ClassRegistration.objects.filter(beginner_class=c, student__in=staff_students)
                for r in cr:
                    if r.student.user.is_instructor:
                        instructors.append(r.student)
                    else:
                        staff.append(r.student)
                class_list.append({'class': c, 'instructors': instructors, 'staff': staff,
                                   'count': crh.enrolled_count(c)})
            logging.debug(class_list)
            self.email.status_email(class_list, staff_query)
            logging.debug('emailed')
