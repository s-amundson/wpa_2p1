import logging
from django.test import TestCase, Client, tag
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Collections

logger = logging.getLogger(__name__)
User = get_user_model()


class TestsCollections(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)


    # @tag('temp')
    def test_get_collections_list(self):
        response = self.client.get(reverse('payment:collections'), secure=True)
        self.assertTemplateUsed(response, 'payment/collection.html')


    # @tag('temp')
    def test_post_collections(self):
        u = User.objects.get(pk=2)
        u.is_board = True
        u.save()

        post_dict = {
            'collected_date': timezone.now(),
            'cash': 30,
            'treasurer': 1,
            'board_member': 2,
            'note': 'test collection'
        }
        response = self.client.post(reverse('payment:collections'), post_dict, secure=True)
        self.assertRedirects(response, reverse('payment:collections'))
        collections = Collections.objects.all()
        self.assertEqual(collections.count(), 1)

    # @tag('temp')
    def test_post_collections_one_board_member(self):
        u = User.objects.get(pk=2)
        u.is_board = True
        u.save()

        post_dict = {
            'collected_date': timezone.now(),
            'cash': 30,
            'treasurer': 1,
            'board_member': 1,
            'note': 'test collection'
        }
        response = self.client.post(reverse('payment:collections'), post_dict, secure=True)
        self.assertEqual(response.status_code, 200)
        collections = Collections.objects.all()
        self.assertEqual(collections.count(), 0)
        self.assertContains(response, 'Fields must not be the same person.')
