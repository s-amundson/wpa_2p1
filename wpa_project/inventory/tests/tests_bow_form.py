import logging
import json
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.apps import apps
from django.utils import timezone

from ..models import Bow

logger = logging.getLogger(__name__)


class TestsBusiness(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # self.minutes = Minutes.objects.create(
        #     meeting_date=timezone.now(),
        #     attending='John, Jane, Jack',
        #     minutes_text='test minutes',
        #     memberships=0,
        #     balance=123.45,
        #     discussion="test discussion"
        # )
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
    def test_get_business(self):
        response = self.client.get(reverse('inventory:bow_form'), secure=True)
        self.assertTemplateUsed('student_app/form_as_p.html')

        # self.assertIn('business', response.context)

    # # @tag('temp')
    # def test_get_business_existing(self):
    #     b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
    #     b1.save()
    #
    #     response = self.client.get(reverse('minutes:business',
    #                                        kwargs={'minutes': self.minutes.id, 'business_id': b1.id}), secure=True)
    #     self.assertTemplateUsed('minutes/forms/business_form.html')
    #     # self.assertIn('business', response.context)
    #     self.assertContains(response, 'Some old test business')
    #     self.assertIsNone(response.context['form']['minutes'].initial)

    # @tag('temp')
    def test_post_business_new(self):
        response = self.client.post(reverse('inventory:bow_form'),
                                    self.post_dict, secure=True)
        b = Bow.objects.last()
        self.assertEqual(len(Bow.objects.all()), 1)
        self.assertEqual(b.bow_id, "R1001")


    # @tag('temp')
    def test_post_business_new2(self):
        self.add_bow()
        response = self.client.post(reverse('inventory:bow_form'),
                                    self.post_dict, secure=True)
        b = Bow.objects.last()
        self.assertEqual(len(Bow.objects.all()), 2)
        self.assertEqual(b.bow_id, "R1004")

    # @tag('temp')
    def test_post_business_existing(self):
        self.add_bow()
        self.post_dict['bow_id'] = 'R1004'
        self.post_dict['in_service'] = False
        response = self.client.post(reverse('inventory:bow_form'),
                                    self.post_dict, secure=True)
        b = Bow.objects.last()
        self.assertEqual(len(Bow.objects.all()), 2)
        self.assertEqual(b.bow_id, "R1004")
        self.assertFalse(b.in_service)

    # # @tag('temp')
    # def test_post_business_existing(self):
    #     b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
    #     b1.save()
    #
    #     self.post_dict['form-0-business'] = b1.id
    #     self.post_dict['form-0-update_text'] = ''
    #
    #     # response = self.client.post(reverse('minutes:business', kwargs={}), d, secure=True)
    #     response = self.client.post(reverse('minutes:business', kwargs={'minutes': self.minutes.id, 'business_id': b1.id}),
    #                                 self.post_dict, secure=True)
    #     b = Business.objects.last()
    #     self.assertEqual(len(Business.objects.all()), 1)
    #     self.assertEqual(b.business, "test business text")
    #     updates = BusinessUpdate.objects.all()
    #     self.assertEqual(updates.count(), 0)
    #
    # # @tag('temp')
    # def test_post_business_existing_resolved(self):
    #     b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
    #     b1.save()
    #     self.assertIsNone(b1.resolved)
    #
    #     self.post_dict['resolved_bool'] = True
    #     self.post_dict['form-0-business'] = b1.id
    #     self.post_dict['form-0-update_text'] = ''
    #
    #     response = self.client.post(reverse('minutes:business', kwargs={'minutes': self.minutes.id, 'business_id': b1.id}),
    #                                 self.post_dict, secure=True)
    #
    #     b = Business.objects.last()
    #     self.assertEqual(len(Business.objects.all()), 1)
    #     self.assertEqual(b.business, "test business text")
    #     logger.warning(b.resolved)
    #     self.assertIsNotNone(b.resolved)
    #
    # # @tag('temp')
    # def test_post_business_existing_unresolved(self):
    #     b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business', resolved='2021-09-04')
    #     b1.save()
    #     self.assertIsNotNone(b1.resolved)
    #
    #     self.post_dict['form-0-business'] = b1.id
    #     # self.post_dict['form-0-update_date'] = ''
    #     self.post_dict['form-0-update_text'] = ''
    #
    #     response = self.client.post(
    #         reverse('minutes:business', kwargs={'minutes': self.minutes.id, 'business_id': b1.id}),
    #         self.post_dict, secure=True)
    #     b = Business.objects.last()
    #     self.assertEqual(len(Business.objects.all()), 1)
    #     self.assertEqual(b.business, "test business text")
    #     self.assertIsNone(b.resolved)
    #
    # # @tag('temp')
    # def test_post_business_update_new(self):
    #     b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
    #     b1.save()
    #
    #     self.post_dict['form-0-business'] = b1.id
    #     self.post_dict['form-0-update_text'] = 'test business text'
    #
    #     response = self.client.post(
    #         reverse('minutes:business', kwargs={'minutes': self.minutes.id, 'business_id': b1.id}),
    #         self.post_dict, secure=True)
    #
    #     b = BusinessUpdate.objects.last()
    #     self.assertEqual(len(BusinessUpdate.objects.all()), 1)
    #     self.assertEqual(b.update_text, "test business text")
    #     # self.assertIsNotNone(b.resolved)
    #
    # # @tag('temp')
    # def test_post_business_update_existing(self):
    #     b1 = Business(minutes=None, added_date='2021-09-04', business='Some old test business')
    #     b1.save()
    #     bu = BusinessUpdate(business=b1, update_text="test update")
    #     bu.save()
    #     self.post_dict['form-INITIAL_FORMS'] = 1
    #     self.post_dict['form-0-business'] = b1.id
    #     self.post_dict['form-0-update_text'] = 'test business text'
    #     self.post_dict['form-0-id'] = bu.id
    #
    #     response = self.client.post(
    #         reverse('minutes:business', kwargs={'minutes': self.minutes.id, 'business_id': b1.id}),
    #         self.post_dict, secure=True)
    #     d = {'business': b1.id, 'update_text': "test business text"}
    #     # response = self.client.post(reverse('minutes:business_update', kwargs={'update_id': bu.id}),
    #     #                             d, secure=True)
    #     b = BusinessUpdate.objects.last()
    #     self.assertEqual(len(BusinessUpdate.objects.all()), 1)
    #     self.assertEqual(b.update_text, "test business text")