import logging

from django.contrib.auth.models import Group
from django.test import TestCase, Client, tag
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Collections
from student_app.models import Student

logger = logging.getLogger(__name__)
User = get_user_model()

# @tag('temp')
class TestsCollections(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.post_dict = {
            'collected_date': timezone.now(),
            'cash': 30,
            'treasurer': 1,
            'board_member': 2,
            'note': 'test collection'
        }

    # @tag('temp')
    def test_get_collections_list(self):
        response = self.client.get(reverse('payment:collections'), secure=True)
        self.assertTemplateUsed(response, 'payment/collection.html')


    # @tag('temp')
    def test_post_collections(self):
        User.objects.get(pk=2).groups.add(Group.objects.get(name='board'))

        response = self.client.post(reverse('payment:collections'), self.post_dict, secure=True)
        self.assertRedirects(response, reverse('payment:collections'))
        collections = Collections.objects.all()
        self.assertEqual(collections.count(), 1)

    # @tag('temp')
    def test_post_collections_one_board_member(self):
        User.objects.get(pk=2).groups.add(Group.objects.get(name='board'))
        self.post_dict['board_member'] = 1

        response = self.client.post(reverse('payment:collections'), self.post_dict, secure=True)
        self.assertEqual(response.status_code, 200)
        collections = Collections.objects.all()
        self.assertEqual(collections.count(), 0)
        self.assertContains(response, 'Fields must not be the same person.')

    # @tag('temp')
    def test_post_collections_correction(self):
        User.objects.get(pk=2).groups.add(Group.objects.get(name='board'))
        self.post_dict['collected_date'] = self.post_dict['collected_date'] - timezone.timedelta(hours=1)
        c = Collections.objects.create(
            collected_date = self.post_dict['collected_date'],
            cash=29,
            treasurer=Student.objects.get(pk=1),
            board_member=Student.objects.get(pk=2),
        )

        response = self.client.post(reverse('payment:collections', kwargs={'pk': c.id}), self.post_dict, secure=True)
        self.assertRedirects(response, reverse('payment:collections'))
        collections = Collections.objects.all().order_by('collected_date')
        self.assertEqual(collections.count(), 2)
        self.assertEqual(collections[0].correction, collections[1].id)
        self.assertIsNone(collections[1].correction)
        self.assertEqual(collections[0].cash, 29)