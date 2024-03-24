import logging
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import PermissionDenied

from django.test import override_settings

from ..models import Reimbursement, ReimbursementItem, ReimbursementVote
from student_app.models import Student
logger = logging.getLogger(__name__)
User = get_user_model()


class TestsReimbursement(TestCase):
    fixtures = ['f1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        # self.post_dict = {'beginning_date': '2022-02-02', 'end_date': '2022-06-06'}
        # self.url = reverse('payment:report')
        self.post_dict = {
            'student': 4,
            'title': 'Test Reimbursement',
            'reimbursementitem_set-TOTAL_FORMS': 5,
            'reimbursementitem_set-INITIAL_FORMS': 1,
            'reimbursementitem_set-MIN_NUM_FORMS': 0,
            'reimbursementitem_set-MAX_NUM_FORMS': 1000,
            'reimbursementitem_set-0-reimbursement': 1,
            'reimbursementitem_set-0-id': 1,
            'reimbursementitem_set-0-description': 'test stuff',
            'reimbursementitem_set-0-amount': 123,
        }
        self.item1 = {
            'reimbursementitem_set-1-reimbursement': 1,
            'reimbursementitem_set-1-description': 'item 1',
            'reimbursementitem_set-1-amount': 12.3,
            'reimbursementitem_set-1-attachment': SimpleUploadedFile("file2.jpg", b"file_content",
                                                                     content_type="image/jpeg")
        }

    def create_reimbursement(self):
        reimbursement = Reimbursement.objects.create(
            status='pending',
            student=Student.objects.get(pk=2),
            title='test title',
        )
        item = ReimbursementItem.objects.create(
            reimbursement=reimbursement,
            amount=123.00,
            description='test stuff',
            attachment=tempfile.NamedTemporaryFile().name
        )

        return reimbursement, item

    def test_get_reimbursement_list(self):
        response = self.client.get(reverse('payment:reimbursement_list'), secure=True)
        self.assertTemplateUsed(response, 'payment/reimbursement_list.html')

    # @tag('temp')
    def test_get_reimbursement_form(self):
        self.client.force_login(User.objects.get(pk=2))
        response = self.client.get(reverse('payment:reimbursement_form'), secure=True)
        self.assertTemplateUsed(response, 'payment/reimbursement_form.html')

    def test_get_reimbursement_form_board(self):
        response = self.client.get(reverse('payment:reimbursement_form'), secure=True)
        self.assertTemplateUsed(response, 'payment/reimbursement_form.html')

    # @tag('temp')
    def test_get_reimbursement_form_existing(self):
        reimbursement = Reimbursement.objects.create(
            status='pending',
            student=Student.objects.get(pk=2),
            title='test title',
        )
        item = ReimbursementItem.objects.create(
            reimbursement=reimbursement,
            amount=123.00,
            description='test stuff',
            attachment=tempfile.NamedTemporaryFile().name
        )
        response = self.client.get(reverse('payment:reimbursement_form', kwargs={'pk': reimbursement.id}), secure=True)
        # logger.warning(response.context['form']['status'])
        self.assertNotContains(response, 'id_status')
        self.assertTemplateUsed(response, 'payment/reimbursement_form.html')

    # @tag('temp')
    def test_get_reimbursement_form_existing_approved(self):
        reimbursement = Reimbursement.objects.create(
            status='approved',
            student=Student.objects.get(pk=2),
            title='test title',
        )
        item = ReimbursementItem.objects.create(
            reimbursement=reimbursement,
            amount=123.00,
            description='test stuff',
            attachment=tempfile.NamedTemporaryFile().name
        )
        response = self.client.get(reverse('payment:reimbursement_form', kwargs={'pk': reimbursement.id}), secure=True)
        self.assertContains(response, 'id_status')
        self.assertTemplateUsed(response, 'payment/reimbursement_form.html')

    # @tag('temp')
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_reimbursement_form(self):
        attach_file = SimpleUploadedFile("file.mp4", b"file_content", content_type="text/plain")
        post_dict = {
            'student': 4,
            'title': 'Test Reimbursement',
            'note': 'test note',
            'reimbursementitem_set-TOTAL_FORMS': 5,
            'reimbursementitem_set-INITIAL_FORMS': 0,
            'reimbursementitem_set-MIN_NUM_FORMS': 0,
            'reimbursementitem_set-MAX_NUM_FORMS': 1000,
            'reimbursementitem_set-0-description': 'item 1',
            'reimbursementitem_set-0-amount': 12.3,
            'reimbursementitem_set-0-attachment': attach_file
        }
        response = self.client.post(reverse('payment:reimbursement_form'), post_dict, secure=True)
        self.assertRedirects(response, reverse('payment:reimbursement_list'))
        reimbursements = Reimbursement.objects.all()
        self.assertEqual(reimbursements.count(), 1)
        self.assertEqual(reimbursements[0].reimbursementitem_set.count(), 1)
        self.assertEqual(reimbursements[0].note, 'test note')
        votes = ReimbursementVote.objects.all()
        self.assertEqual(votes.count(), 0)

        vote_count = ReimbursementVote.objects.get_vote_count(reimbursements[0])
        self.assertEqual(vote_count, {'yes': 0, 'no': 0})

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_reimbursement_form_board(self):
        attach_file = SimpleUploadedFile("file.mp4", b"file_content", content_type="text/plain")
        post_dict = {
            'student': 1,
            'title': 'Test Reimbursement',
            'note': 'test note',
            'reimbursementitem_set-TOTAL_FORMS': 5,
            'reimbursementitem_set-INITIAL_FORMS': 0,
            'reimbursementitem_set-MIN_NUM_FORMS': 0,
            'reimbursementitem_set-MAX_NUM_FORMS': 1000,
            'reimbursementitem_set-0-description': 'item 1',
            'reimbursementitem_set-0-amount': 12.3,
            'reimbursementitem_set-0-attachment': attach_file
        }
        response = self.client.post(reverse('payment:reimbursement_form'), post_dict, secure=True)
        self.assertRedirects(response, reverse('payment:reimbursement_list'))
        reimbursements = Reimbursement.objects.all()
        self.assertEqual(reimbursements.count(), 1)
        self.assertEqual(reimbursements[0].reimbursementitem_set.count(), 1)
        self.assertEqual(reimbursements[0].note, 'test note')
        votes = ReimbursementVote.objects.all()
        self.assertEqual(votes.count(), 1)

        vote_count = ReimbursementVote.objects.get_vote_count(reimbursements[0])
        self.assertEqual(vote_count, {'yes': 1, 'no': 0})

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_ammend_reimbursement_form(self):
        r, ri = self.create_reimbursement()

        response = self.client.post(reverse('payment:reimbursement_form', kwargs={'pk': r.id}),
                                    self.post_dict | self.item1, secure=True)
        self.assertRedirects(response, reverse('payment:reimbursement_list'))

        reimbursements = Reimbursement.objects.all()
        self.assertEqual(reimbursements.count(), 1)
        self.assertEqual(reimbursements[0].reimbursementitem_set.count(), 2)
        self.assertNotEquals(r.modified, reimbursements[0].modified)

    # # @tag('temp')
    # @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    # def test_post_ammend_reimbursement_form_approved(self):
    #     r, ri = self.create_reimbursement()
    #     r.status = 'approved'
    #     r.save()
    #     self.post_dict['status'] = 'paid'
    #     response = self.client.post(reverse('payment:reimbursement_form', kwargs={'pk': r.id}),
    #                                 self.post_dict, secure=True)
    #     self.assertRedirects(response, reverse('payment:reimbursement_list'))
    #
    #     reimbursements = Reimbursement.objects.all()
    #     self.assertEqual(reimbursements.count(), 1)
    #     self.assertEqual(reimbursements[0].reimbursementitem_set.count(), 2)
    #     self.assertNotEquals(r.modified, reimbursements[0].modified)

    def test_get_reimbursement_vote(self):
        r, ri = self.create_reimbursement()
        response = self.client.get(reverse('payment:reimbursement_vote', kwargs={'pk': r.id}), secure=True)
        self.assertTemplateUsed(response, 'payment/reimbursement_vote.html')

    def test_post_reimbursement_vote_approve(self):
        r, ri = self.create_reimbursement()

        for i in range(3):
            ReimbursementVote.objects.create(
                reimbursement=r,
                student=Student.objects.get(pk=3+i),
                approve=True
            )
        post_dict = {
            'reimbursement': r.id,
            'student': 1,
            'approve': True
        }
        response = self.client.post(reverse('payment:reimbursement_vote', kwargs={'pk': r.id}), post_dict, secure=True)

        votes = ReimbursementVote.objects.all()
        r2 = Reimbursement.objects.get(pk=r.id)
        self.assertEqual(votes.count(), 4)
        self.assertEqual(r2.status, 'approved')
        self.assertEqual(r.modified, r2.modified)

    def test_post_reimbursement_vote_denied(self):
        r, ri = self.create_reimbursement()

        for i in range(3):
            ReimbursementVote.objects.create(
                reimbursement=r,
                student=Student.objects.get(pk=3+i),
                approve=False
            )
        post_dict = {
            'reimbursement': r.id,
            'student': 1,
            'approve': False
        }
        response = self.client.post(reverse('payment:reimbursement_vote', kwargs={'pk': r.id}), post_dict, secure=True)

        votes = ReimbursementVote.objects.all()
        r2 = Reimbursement.objects.get(pk=r.id)
        self.assertEqual(votes.count(), 4)
        self.assertEqual(r2.status, 'denied')
        self.assertEqual(r.modified, r2.modified)

    def test_vote_self(self):
        r, ri = self.create_reimbursement()
        r.student = Student.objects.get(pk=1)
        r.save()

        post_dict = {
            'reimbursement': r.id,
            'student': 1,
            'approve': False
        }
        response = self.client.post(reverse('payment:reimbursement_vote', kwargs={'pk': r.id}), post_dict, secure=True)
        self.assertRedirects(response, reverse('payment:reimbursement_list'))
        # self.assertEqual(response.status_code, 403)
        votes = ReimbursementVote.objects.all()
        r2 = Reimbursement.objects.get(pk=r.id)
        self.assertEqual(votes.count(), 1)
        self.assertEqual(r2.status, 'pending')
        self.assertEqual(r.modified, r2.modified)

    def test_vote_twice(self):
        r, ri = self.create_reimbursement()

        ReimbursementVote.objects.create(
            reimbursement=r,
            student=Student.objects.get(pk=1),
            approve=False
        )

        post_dict = {
            'reimbursement': r.id,
            'student': 1,
            'approve': False
        }
        response = self.client.post(reverse('payment:reimbursement_vote', kwargs={'pk': r.id}), post_dict, secure=True)
        self.assertRedirects(response, reverse('payment:reimbursement_list'))

        votes = ReimbursementVote.objects.all()
        r2 = Reimbursement.objects.get(pk=r.id)
        self.assertEqual(votes.count(), 1)
        self.assertEqual(r2.status, 'pending')
        self.assertEqual(r.modified, r2.modified)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_vote_then_update(self):
        r, ri = self.create_reimbursement()
        v = ReimbursementVote.objects.create(
            reimbursement=r,
            student=Student.objects.get(pk=2),
            approve=True
        )

        vote_count = ReimbursementVote.objects.get_vote_count(r)
        self.assertEqual(vote_count, {'yes': 1, 'no': 0})

        response = self.client.post(reverse('payment:reimbursement_form', kwargs={'pk': r.id}),
                                    self.post_dict | self.item1, secure=True)
        self.assertRedirects(response, reverse('payment:reimbursement_list'))

        reimbursements = Reimbursement.objects.all()
        self.assertEqual(reimbursements.count(), 1)
        self.assertEqual(reimbursements[0].reimbursementitem_set.count(), 2)
        vote_count = ReimbursementVote.objects.get_vote_count(reimbursements[0])
        self.assertEqual(vote_count, {'yes': 0, 'no': 0})
