from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
import logging

from ..forms import ThemeForm
from ..models import Student
logger = logging.getLogger(__name__)


class ProfileView(LoginRequiredMixin, View):
    """Shows the users profile"""
    def get(self, request):
        try:
            s = Student.objects.get(user=request.user)
            # logging.debug(s)
            student_family = s.student_family
            this_student = s
        except Student.DoesNotExist:  # pragma: no cover
            student_family = None
            this_student = None
        theme = ThemeForm(initial={'theme': 'dark' if request.user.dark_theme else 'light'})
        if student_family is not None:
            students = student_family.student_set.all()
            d = {'students': students, 'theme_form': theme, 'student_family': student_family,
                 'this_student': this_student}
            return render(request, 'student_app/profile.html', d)
        else:
            # return HttpResponseRedirect(reverse('registration:student_register'))
            return render(request, 'student_app/profile.html', {'theme_form': theme, 'this_student': this_student})

