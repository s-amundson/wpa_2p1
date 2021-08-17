# runapscheduler.py
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date, timedelta
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.utils import timezone
logger = logging.getLogger(__name__)


#@util.ensure_old_connections_are_closed
def my_job():
    # Get our model
    m = apps.get_model(app_label='student_app', model_name='BeginnerClass')
    states = m().get_states()

    # close tomorrows class
    d = date.today() + timedelta(days=1)
    bc = m.objects.filter(class_date__lte=d, state__in=states[:3])
    bc.state = states[3]  # 'closed'
    bc.save()

    # # open next weeks class
    # d = date.today() + timedelta(days=6)
    # bc = m.objects.filter(class_date__lte=d, state=states[0])
    # bc.state = states[1]  # 'open'

    # create class day after tomorrow and open
    d = date.today() + timedelta(days=2)
    d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
    bc = m(class_date=d, beginner_limit=10, returnee_limit=10, state='open')
    bc.save()
    # bc = m.create(class_date=d + timedelta(hours=2), beginner_limit=0, returnee_limit=10, state='open')
    # bc.save()


# The `ensure_old_connections_are_closed` decorator ensures that database connections, that
# have become unusable or are obsolete, are closed before and after our job has run.
#
# It is only required when your job needs to access the database and you are NOT making use
# of a database connection pooler.
# @util.ensure_old_connections_are_closed
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes all APScheduler job executions older than `max_age` from the database.

    :param max_age: The maximum length of time to retain old job execution records. Defaults
                    to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(hour="06", minute="25"),  # Every day at midnight
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        # scheduler.add_job(
        #     delete_old_job_executions,
        #     trigger=CronTrigger(
        #         day_of_week="mon", hour="00", minute="00"
        #     ),  # Midnight on Monday, before start of the next work week.
        #     id="delete_old_job_executions",
        #     max_instances=1,
        #     replace_existing=True,
        # )
        # logger.info(
        #     "Added weekly job: 'delete_old_job_executions'."
        # )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
