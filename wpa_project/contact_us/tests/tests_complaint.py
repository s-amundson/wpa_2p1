import logging

from django.apps import apps
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.utils import timezone
from _email.models import BulkEmail

from ..models import Category, Message, Complaint

logger = logging.getLogger(__name__)
User = apps.get_model('student_app', 'User')


class TestsComplaint(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.post_dict = {
            'category': 'services',
            'incident_date': '2021-05-31',
            'message': 'test message',
            'anonymous': True,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        self.complaint = None

    def add_message(self):
        self.complaint = Complaint.objects.create(
            category='services',
            incident_date="2021-05-31",
            message='test message')

    # @tag('temp')
    def test_get_complaint_user(self):
        self.client.force_login(User.objects.get(pk=3))
        response = self.client.get(reverse('contact_us:complaint'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us/complaint.html')
        logging.warning(response.context)

    # @tag('temp')
    def test_get_complaint_board_existing_good(self):
        self.add_message()
        response = self.client.get(reverse('contact_us:complaint', kwargs={'pk': self.complaint.id}), secure=True)
        self.assertEqual(response.status_code, 200)

    # @tag('temp')
    def test_get_complaint_user_existing_no_auth(self):
        self.client.force_login(User.objects.get(pk=3))
        self.add_message()
        response = self.client.get(reverse('contact_us:complaint', kwargs={'pk': self.complaint.id}), secure=True)
        self.assertEqual(response.status_code, 403)

    # @tag('temp')
    def test_post_complaint_user_anonymous(self):
        self.client.force_login(User.objects.get(pk=3))
        response = self.client.post(reverse('contact_us:complaint'), self.post_dict, secure=True)

        self.assertRedirects(response, reverse('contact_us:thanks'))
        be = BulkEmail.objects.all()
        self.assertEqual(len(be), 1)
        self.assertTrue(be[0].body.find('anonymously') > 0)
        self.assertIsNone(Complaint.objects.last().resolved_date)

    # @tag('temp')
    def test_post_complaint_user_not_anonymous(self):
        self.client.force_login(User.objects.get(pk=3))
        self.post_dict['anonymous'] = False
        response = self.client.post(reverse('contact_us:complaint'), self.post_dict, secure=True)

        self.assertRedirects(response, reverse('contact_us:thanks'))
        be = BulkEmail.objects.all()
        self.assertEqual(len(be), 1)
        logger.warning(be[0].body)
        self.assertFalse(be[0].body.find('anonymously') > 0)
        self.assertTrue(be[0].body.find('Charles Wells') > 0)
        self.assertIsNone(Complaint.objects.last().resolved_date)

    # @tag('temp')
    def test_post_complaint_resolved(self):
        self.add_message()
        self.post_dict['form-0-complaint'] = self.complaint.id,
        self.post_dict['form-0-comment'] = 'test comment',
        self.post_dict['form-0-comment_date'] = timezone.now()
        self.post_dict['form-0-id'] = ''
        self.post_dict['resolved'] = True
        response = self.client.post(reverse('contact_us:complaint', kwargs={'pk': self.complaint.id}), self.post_dict, secure=True)
        complaints = Complaint.objects.all()
        self.assertEqual(complaints.count(), 1)
        self.assertGreater(complaints.last().resolved_date, self.post_dict['form-0-comment_date'])