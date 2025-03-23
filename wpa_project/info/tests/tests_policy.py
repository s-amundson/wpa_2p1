import logging
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone
from student_app.models import User
from ..models import Announcement, Policy, PolicyText
logger = logging.getLogger(__name__)


class TestsAnnouncement(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)

    # @tag('temp')
    def test_get_announcement_form(self):
        response = self.client.get(reverse('information:policy'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/policy.html')

    # @tag('temp')
    def test_post_board_draft_good(self):
        response = self.client.post(reverse('information:policy'), {
            'title_text': 'test policy',
            'status': 0,
            'is_html': False,
            'policy': "tests shall be done"})

        pt = PolicyText.objects.all()
        self.assertEqual(len(pt), 1)
        self.assertEqual(pt[0].policy, 'tests shall be done')
        self.assertEqual(pt[0].title.title, 'test policy')

    # @tag('temp')
    def test_post_board_update_good(self):
        policy = Policy.objects.create(title='test policy')
        pt1 = PolicyText.objects.create(
            title=policy,
            status=0,
            is_html=False,
            policy='tests can be done'
        )
        response = self.client.post(reverse('information:policy', kwargs={'policy': policy.id}), {
            'title_text': 'test policy',
            'status': 1,
            'is_html': False,
            'policy': "tests shall be done"})

        polices = Policy.objects.all()
        pt = PolicyText.objects.all()
        self.assertEqual(len(polices), 1)
        self.assertEqual(len(pt), 2)
        self.assertEqual(pt[0].policy, 'tests shall be done')
        self.assertEqual(pt[0].title.title, 'test policy')
        self.assertEqual(pt[0].status, 1)
