import logging
import json
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.apps import apps
from django.utils import timezone

from ..models import Bow, BowInventory

logger = logging.getLogger(__name__)


class TestsBowInventory(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        self.post_dict = {'user': self.test_user, 'bow_id': 'R1003'}

    def add_bow(self):
        return Bow.objects.create(
            bow_id='R1003',
            hand='R',
            poundage=10,
            length=54,
            type='TDR',
            riser_material='wood',
            riser_manufacturer='Acme',
            riser_color='Natural',
            limb_color='White',
            limb_manufacturer='Acme',
            limb_model='Rabbit',
            in_service=True
        )

    # @tag('temp')
    def test_get_bow_inventory(self):
        response = self.client.get(reverse('inventory:bow_inventory'), secure=True)
        self.assertTemplateUsed('student_app/barcode.html')

    # @tag('temp')
    def test_post_inventory(self):
        b = self.add_bow()
        response = self.client.post(reverse('inventory:bow_inventory'),
                                    {'user': self.test_user.id, 'bow_id': 'R1003'}, secure=True)
        inventory = BowInventory.objects.all()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].bow.bow_id, "R1003")
