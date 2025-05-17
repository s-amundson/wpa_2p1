import logging
import time

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.apps import apps
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from ..tasks import close_poll
from ..models import Business, Minutes, Poll, PollType, PollChoices, PollVote

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

    def create_poll(self):
        poll = Poll.objects.create(
            description='test motion',
            poll_type=PollType.objects.get(pk=2),
            level='board',
            state='open',
        )
        poll.poll_choices.set(PollChoices.objects.all()[:3])
        return poll

    # @tag('temp')
    def test_get_poll(self):
        response = self.client.get(reverse('minutes:poll'), secure=True)
        self.assertTemplateUsed('minutes/forms/poll_form.html')
        self.assertEqual(response.context['form'].fields['poll_choices'].queryset.count(), 5)
        self.assertEqual(response.context['form'].initial['poll_type'].poll_type, 'poll')
        self.assertEqual(response.context['poll_type'], 'poll')

    # @tag('temp')
    def test_get_poll_with_type_motion(self):
        response = self.client.get(reverse('minutes:poll') + '?poll_type=motion', secure=True)
        self.assertTemplateUsed('minutes/forms/poll_form.html')
        self.assertTemplateUsed('minutes/poll.html')
        self.assertEqual(response.context['form'].fields['poll_choices'].queryset.count(), 3)
        self.assertEqual(response.context['form'].initial['poll_type'].poll_type, 'motion')
        self.assertEqual(response.context['poll_type'], 'motion')

    # @tag('temp')
    def test_get_poll_list(self):
        response = self.client.get(reverse('minutes:poll_list'), secure=True)
        self.assertTemplateUsed('minutes/poll_list.html')
        self.assertEqual(response.context['poll_type'], 'poll')

    # @tag('temp')
    def test_get_poll_list_motion(self):
        p = self.create_poll()
        pv = PollVote.objects.create(poll=p, user=self.test_user, choice=PollChoices.objects.get(pk=1))
        p.state = 'closed'
        p.save()
        response = self.client.get(reverse('minutes:poll_list') + '?poll_type=motion', secure=True)
        self.assertTemplateUsed('minutes/poll_list.html')
        self.assertEqual(response.context['poll_type'], 'motion')
        self.assertContains(response, 'Results: Aye 1')

    # @tag('temp')
    def test_post_motion(self):
        response = self.client.post(reverse('minutes:poll') + '?poll_type=motion', self.post_dict, secure=True)
        polls = Poll.objects.all()
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls[0].poll_type.poll_type, 'motion')
        self.assertIsNone(polls[0].minutes)
        self.assertIsNone(polls[0].business)
        self.assertEqual(CrontabSchedule.objects.all().count(), 1)
        self.assertEqual(PeriodicTask.objects.all().count(), 1)

    # @tag('temp')
    def test_post_motion_update(self):
        m = self.create_poll()
        time.sleep(.5)
        response = self.client.post(reverse('minutes:poll', kwargs={'pk': m.id}) + '?poll_type=motion', self.post_dict, secure=True)
        polls = Poll.objects.all()
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls[0].poll_type.poll_type, 'motion')
        self.assertIsNone(polls[0].minutes)
        self.assertIsNone(polls[0].business)
        self.assertEqual(m.poll_date, polls[0].poll_date)
        self.assertEqual(CrontabSchedule.objects.all().count(), 1)
        self.assertEqual(PeriodicTask.objects.all().count(), 1)

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
        response = self.client.post(reverse('minutes:poll') + '?poll_type=motion', self.post_dict, secure=True)
        self.assertEqual(len(Poll.objects.all()), 1)
        self.assertEqual(Poll.objects.last().business.id, b1.id)
        self.assertEqual(Poll.objects.last().minutes.id, m.id)

    # @tag('temp')
    def test_get_poll_vote(self):
        p = self.create_poll()
        response = self.client.get(reverse('minutes:poll_vote', kwargs={'poll': p.id}), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('minutes/poll.html')
        self.assertTemplateUsed('minutes/forms/poll_vote_form.html')

    # @tag('temp')
    def test_post_poll_vote(self):
        p = self.create_poll()
        response = self.client.post(reverse('minutes:poll_vote', kwargs={'poll': p.id}),
                                    {'poll': p.id, 'choice': 1, 'user': self.test_user.id}, secure=True)
        self.assertRedirects(response, reverse('minutes:poll_list') + '?poll_type=motion')
        pv = PollVote.objects.all()
        self.assertEqual(pv.count(), 1)
        self.assertEqual(pv.last().choice.id, 1)

        response = self.client.post(reverse('minutes:poll_vote', kwargs={'poll': p.id}),
                                    {'poll': p.id, 'choice': 2, 'user': self.test_user.id}, secure=True)
        pv = PollVote.objects.all()
        self.assertEqual(pv.count(), 1)
        self.assertEqual(pv.last().choice.id, 2)

    # @tag('temp')
    def test_task_close_poll(self):
        p = self.create_poll()
        close_poll(p.id)
        polls = Poll.objects.all()
        self.assertEqual(len(polls), 1)
        self.assertEqual(polls.last().poll_type.poll_type, 'motion')
        self.assertEqual(polls.last().state,'closed')
