import logging
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from student_app.models import User
from ..models import Announcement
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

    def test_get_announcement_list(self):
        d = timezone.now() - timezone.timedelta(days=20)

        Announcement.objects.create(
            begin_date=timezone.now() - timezone.timedelta(days=20),
            end_date=timezone.now() + timezone.timedelta(days=10),
            announcement="Doing something",
            status=1)
        Announcement.objects.create(
            begin_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=20),
            announcement="Doing something else",
            status=1)
        self.client.logout()
        response = self.client.get(reverse('information:announcement_list'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['announcements']), 2)

    def test_get_announcement_form(self):
        response = self.client.get(reverse('information:announcement_form'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/preview_form.html')

    def test_post_staff_profile_form(self):
        response = self.client.post(reverse('information:announcement_form'), {
            'begin_date': timezone.now() - timezone.timedelta(days=20),
            'end_date': timezone.now() + timezone.timedelta(days=10),
            'announcement': "Doing something",
            'status': 1})

        announcements = Announcement.objects.all()
        self.assertEqual(len(announcements), 1)
        self.assertEqual(announcements[0].announcement, 'Doing something')

    def test_post_staff_profile_form_id(self):
        announcement = Announcement.objects.create(
            begin_date=timezone.now() - timezone.timedelta(days=20),
            end_date=timezone.now() + timezone.timedelta(days=10),
            announcement="Doing something",
            status=1)

        logger.warning(announcement.id)
        response = self.client.post(reverse('information:announcement_form', kwargs={'pk': announcement.id}),{
            'begin_date': timezone.now() - timezone.timedelta(days=20),
            'end_date': timezone.now() + timezone.timedelta(days=10),
            'announcement': "Doing something",
            'status': 2}, secure=True)
        announcements = Announcement.objects.all()
        self.assertEqual(len(announcements), 1)
        self.assertEqual(announcements[0].status, 2)
