from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy


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
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.student_set.last() is None or request.user.student_set.last().student_family is None:
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))
        return super().dispatch(request, *args, **kwargs)