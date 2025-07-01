import logging

from django.contrib.auth.models import Group
from django.test import TestCase, Client, tag
from django.urls import reverse

from ..models import User
logger = logging.getLogger(__name__)

# @tag('temp')
class TestsUserView(TestCase):
    fixtures = ['f1']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.test_user = User.objects.get(pk=1)
        self.client.force_login(self.test_user)
        self.post_dict = {'is_board': False, 'is_staff': True, 'is_instructor': False,
                          'dark_theme': True, 'is_active': True, 'is_member': False}
        self.url = reverse('registration:update_user', kwargs={'user_id': 4})

    def test_get_user_view_invalid(self):
        # Get the page, if not super or board, page is forbidden
        self.test_user = User.objects.get(pk=3)
        self.client.force_login(self.test_user)
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed('student_app/index.html')

    def test_get_user_view_valid(self):
        # Get the page, if not super or board, page is forbidden
        response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('student_app/form_as_p.html')

    def test_post_user_view_valid(self):
        # Post the page, if not super or board, page is forbidden
        user = User.objects.get(pk=4)
        self.assertFalse(user.dark_theme)
        response = self.client.post(self.url, self.post_dict, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        user = User.objects.get(pk=4)
        self.assertTrue(user.dark_theme)

    @tag('temp')
    def test_post_user_remove_groups(self):
        user = User.objects.get(pk=4)
        user.groups.add(Group.objects.get(name='instructors'))
        user.groups.add(Group.objects.get(name='board'))
        response = self.client.post(self.url, self.post_dict, secure=True)
        self.assertRedirects(response, reverse('registration:profile'))
        user = User.objects.get(pk=4)
        self.assertFalse(user.has_perm('student_app.board'))
        self.assertFalse(user.has_perm('student_app.instructors'))
        self.assertTrue(user.has_perm('student_app.staff'))