import logging
import json
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.apps import apps
from django.utils import timezone

from ..models import Bow

logger = logging.getLogger(__name__)


class TestsBowForm(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)

        self.post_dict = {
            'hand': 'R',
            'poundage': 10,
            'length': 54,
            'type': 'TDR',
            'riser_material': 'wood',
            'riser_manufacturer': 'Acme',
            'riser_color': 'Natural	',
            'limb_color': 'White',
            'limb_manufacturer': 'Acme',
            'limb_model': 'Rabbit',
            'in_service': True,
        }
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
    def test_get_bow_form(self):
        response = self.client.get(reverse('inventory:bow_form'), secure=True)
        self.assertTemplateUsed('student_app/form_as_p.html')

    # @tag('temp')
    def test_post_bow_new(self):
        response = self.client.post(reverse('inventory:bow_form'),
                                    self.post_dict, secure=True)
        b = Bow.objects.last()
        self.assertEqual(len(Bow.objects.all()), 1)
        self.assertEqual(b.bow_id, "R1001")


    # @tag('temp')
    def test_post_bow_new2(self):
        self.add_bow()
        response = self.client.post(reverse('inventory:bow_form'),
                                    self.post_dict, secure=True)
        b = Bow.objects.last()
        self.assertEqual(len(Bow.objects.all()), 2)
        self.assertEqual(b.bow_id, "R1004")

    # @tag('temp')
    def test_post_bow_existing(self):
        self.add_bow()
        self.post_dict['bow_id'] = 'R1004'
        self.post_dict['in_service'] = False
        response = self.client.post(reverse('inventory:bow_form'),
                                    self.post_dict, secure=True)
        b = Bow.objects.last()
        self.assertEqual(len(Bow.objects.all()), 2)
        self.assertEqual(b.bow_id, "R1004")
        self.assertFalse(b.in_service)

    # @tag('temp')
    def test_post_bow_update_existing(self):
        b = self.add_bow()
        self.post_dict['bow_id'] = 'R1003'
        self.post_dict['in_service'] = False
        response = self.client.post(reverse('inventory:bow_form', kwargs={'pk': b.id}),
                                    self.post_dict, secure=True)
        b = Bow.objects.last()
        self.assertEqual(len(Bow.objects.all()), 1)
        self.assertEqual(b.bow_id, "R1003")
        self.assertFalse(b.in_service)
