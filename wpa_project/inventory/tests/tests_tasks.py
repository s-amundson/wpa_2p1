import logging

from django.test import TestCase, tag
from ..models import Bow
from ..tasks import inventory_from_csv
logger = logging.getLogger(__name__)

# @tag('temp')
class TestsTasks(TestCase):

    # @tag('temp')
    def test_add_inventory(self):

        inventory_from_csv()
        bows = Bow.objects.all()
        self.assertEqual(bows.count(), 243)


