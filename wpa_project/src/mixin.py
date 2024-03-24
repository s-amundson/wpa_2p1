from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)


class BoardMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False


class StaffMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        return False


class StudentFamilyMixin(AccessMixin):
    def __init__(self):
        self.student_family = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.student_set.last() is None or request.user.student_set.last().student_family is None:
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))
        self.student_family = request.user.student_set.last().student_family
        return super().dispatch(request, *args, **kwargs)


class MemberMixin(StudentFamilyMixin):
    def __init__(self):
        self.member = None

    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        self.member = request.user.student_set.last().member_set.last()
        logger.warning(self.member)
        if self.member.expire_date >= timezone.now().date():
            return dispatch
        return self.handle_no_permission()