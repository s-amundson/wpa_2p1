import logging
import time
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from ..models import BeginnerClass
from ..src import UpdatePrograms
logger = logging.getLogger(__name__)


class TestsUpdatePrograms(TestCase):

    def test_beginner_class(self):
        d = timezone.localtime(timezone.now()).date() + timedelta(days=1)
        d = timezone.datetime(year=d.year, month=d.month, day=d.day, hour=9)
        bc = BeginnerClass(class_date=d, class_type='combined', beginner_limit=10, returnee_limit=10, state='open')
        bc.save()
        # d = timezone.datetime(year=d.year, month=d.month, day=25, hour=9)
        # bc = BeginnerClass(class_date=d, class_type='combined', beginner_limit=10, returnee_limit=10, state='open')
        # bc.save()

        UpdatePrograms().beginner_class()

        self.assertEqual(BeginnerClass.objects.all().count(), 9)
        self.assertEqual(BeginnerClass.objects.get(pk=bc.id).state, 'closed')
        for i in range(8):
            # self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 1 + i).state, 'open')
            self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 1 + i).state, 'open')
        # self.assertEqual(BeginnerClass.objects.get(pk=bc.id + 2).state, 'open')

