import logging
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.apps import apps

from ..models import Business, Minutes,Poll

logger = logging.getLogger(__name__)


class TestsReport(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.User = apps.get_model(app_label='student_app', model_name='User')


    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = self.User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # pt, created = PollType.objects.get_or_create(poll_type='motion')
        self.post_dict = {
            'description': 'test motion',
            'poll_choices': [1, 2, 3],
            'level': 'board',
            'state': 'open',
            'duration': 1,
            'is_anonymous': False,
            'minutes': '',
            'business': '',
            'poll_type': 2
        }

    # @tag('temp')
    def test_get_poll(self):
        response = self.client.get(reverse('minutes:poll'), secure=True)
        self.assertTemplateUsed('minutes/poll_form.html')
        self.assertEqual(response.context['form'].fields['poll_choices'].queryset.count(), 5)
        self.assertEqual(response.context['form'].initial['poll_type'].poll_type, 'poll')
        self.assertEqual(response.context['poll_type'], 'poll')

    # @tag('temp')
    def test_get_poll_with_type_motion(self):
        response = self.client.get(reverse('minutes:poll') + '?poll_type=motion', secure=True)
        self.assertTemplateUsed('minutes/poll_form.html')
        self.assertEqual(response.context['form'].fields['poll_choices'].queryset.count(), 3)
        self.assertEqual(response.context['form'].initial['poll_type'].poll_type, 'motion')
        self.assertEqual(response.context['poll_type'], 'motion')

    # @tag('temp')
    def test_get_motion(self):
        response = self.client.get(reverse('minutes:motion'), secure=True)
        self.assertTemplateUsed('minutes/poll_form.html')
        # self.assertEqual(response.context['form'].fields['poll_choices'].queryset.count(), 3)
        # self.assertEqual(response.context['form'].initial['poll_type'].poll_type, 'motion')
        # self.assertEqual(response.context['poll_type'], 'motion')

    @tag('temp')
    def test_post_motion(self):
        response = self.client.post(reverse('minutes:poll'), self.post_dict, secure=True)
        self.assertEqual(len(Poll.objects.all()), 1)


    # @tag('temp')
    def test_post_motion_minutes_and_business(self):
        m = Minutes(
            meeting_date='2021-09-04T19:20:30+03:00', attending='', minutes_text='', memberships=0,
            balance=0, discussion='', end_time=None,
        )
        m.save()
        b1 = Business(minutes=m, added_date='2021-09-04', business='Some old test business')
        b1.save()

        self.post_dict['minutes'] = m.id
        self.post_dict['business'] = b1.id
        response = self.client.post(reverse('minutes:motion'), self.post_dict, secure=True)
        self.assertEqual(len(Poll.objects.all()), 1)
        self.assertEqual(Poll.objects.last().business.id, b1.id)
