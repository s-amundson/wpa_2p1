import logging
from django.test import TestCase, Client

from ..models import Event, VolunteerRecord
from student_app.models import Student

logger = logging.getLogger(__name__)


class TestsOther(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_update_points(self):
        VolunteerRecord.objects.update_points(Event.objects.get(pk=1), Student.objects.get(pk=1), 2)
        records = VolunteerRecord.objects.all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].volunteer_points, 2)

        VolunteerRecord.objects.update_points(Event.objects.get(pk=1), Student.objects.get(pk=1), 5)
        records = VolunteerRecord.objects.all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].volunteer_points, 5)

        VolunteerRecord.objects.update_points(Event.objects.get(pk=1), Student.objects.get(pk=1), 0)
        records = VolunteerRecord.objects.all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].volunteer_points, 0)

    def test_update_points_zero(self):
        VolunteerRecord.objects.update_points(Event.objects.get(pk=1), Student.objects.get(pk=1), 0)
        records = VolunteerRecord.objects.all()
        self.assertEqual(len(records), 0)