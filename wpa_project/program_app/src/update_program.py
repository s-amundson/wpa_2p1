import logging
from django.utils import timezone
from datetime import timedelta
from ..models import BeginnerClass, BeginnerSchedule, ClassRegistration
from ..src import ClassRegistrationHelper, EmailMessage
from student_app.models import Student, User

logger = logging.getLogger(__name__)


def close_class_job(class_time):
    UpdatePrograms().close_class(class_time)


def reminder_email_job(class_time):
    UpdatePrograms().reminder_email(class_time)


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

    def create_class(self, beginner_schedule):
        class_date = timezone.datetime.combine(
            self.today + timedelta(days=(7 * beginner_schedule.frequency * beginner_schedule.future_classes) + 1),
            beginner_schedule.class_time)
        bc, created = BeginnerClass.objects.get_or_create(
            class_date=class_date,
            class_type=beginner_schedule.class_type,
            beginner_limit=beginner_schedule.beginner_limit,
            beginner_wait_limit=beginner_schedule.beginner_wait_limit,
            returnee_limit=beginner_schedule.returnee_limit,
            returnee_wait_limit=beginner_schedule.returnee_wait_limit,
            state=beginner_schedule.state)

    def close_class(self, class_time):
        class_date = timezone.datetime.combine(self.today + timedelta(days=1), class_time)
        classes = BeginnerClass.objects.filter(
            class_date=class_date, state__in=self.states[:self.states.index('closed')])
        for c in classes:
            c.state = self.states[self.states.index('closed')]  # 'closed'
            c.save()
            # logging.debug(c.state)

    def daily_update(self):
        # self.add_weekly()
        self.status_email()
        self.record_classes()

    def next_class_day(self, target_day):
        """Returns the next eligible class day (not today or tomorrow)
        target_day is  0-6. Monday is 0 and Sunday is 6"""
        target_day = target_day % 7
        target_delta = target_day - self.today.weekday()
        while target_delta <= 1:
            target_delta += 7
        return self.today + timedelta(target_delta)

    def record_classes(self):
        # set past classes to recorded
        yesterday = self.today - timedelta(days=1)
        classes = BeginnerClass.objects.filter(
            class_date__lte=yesterday, state__in=self.states[:self.states.index('recorded')])
        for c in classes:
            c.state = 'recorded'
            c.save()

    def reminder_email(self, class_time):
        # send reminder email to students for classes 2 days from now.
        staff_query = User.objects.filter(is_staff=True, is_active=True)
        class_date = timezone.datetime.combine(self.today + timedelta(days=2), class_time)
        classes = BeginnerClass.objects.filter(
            class_date=class_date, state__in=self.states[:self.states.index('closed')])
        for c in classes:
            # send email to students that are registered
            cr = c.classregistration_set.filter(pay_status__in=['paid', 'admin'])
            student_list = []
            for r in cr:
                student_list.append(r.student.id)
            students = Student.objects.filter(id__in=student_list)
            students = students.exclude(user__in=staff_query)
            # logging.debug(students)
            self.email.beginner_reminder(c, students)

            # send email to students that are on the wait list
            cr = c.classregistration_set.filter(pay_status__in=['waiting'])
            student_list = []
            for r in cr:
                student_list.append(r.student.id)
            students = Student.objects.filter(id__in=student_list)
            students = students.exclude(user__in=staff_query)
            self.email.wait_list_reminder(c, students)

    def status_email(self):
        crh = ClassRegistrationHelper()
        email_date = self.today + timedelta(days=3)
        # logging.debug(email_date)
        staff_query = User.objects.filter(is_staff=True, is_active=True)
        staff_students = Student.objects.filter(user__in=staff_query)
        classes = BeginnerClass.objects.filter(
            class_date__date=email_date, state__in=self.states[:self.states.index('closed')])
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
            # logging.debug(class_list)
            self.email.status_email(class_list, staff_query)
            # logging.debug('emailed')
