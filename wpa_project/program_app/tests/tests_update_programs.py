import logging
import time
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from ..models import BeginnerClass
from ..src import UpdatePrograms
logger = logging.getLogger(__name__)


class TestsUpdatePrograms(TestCase):
    # fixtures = ['f1']

    def test_beginner_class(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        bc = BeginnerClass(class_date=d, beginner_limit=10, returnee_limit=10, state='open')
        bc.save()
        logging.debug(d)

        UpdatePrograms().beginner_class()

        self.assertEqual(BeginnerClass.objects.all().count(), 2)
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).state, 'closed')
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 1).state, 'open')
