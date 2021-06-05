from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
import logging

from ..models import StudentFamily, Student
logger = logging.getLogger(__name__)


class ProfileView(LoginRequiredMixin, View):
    """Shows a message page"""
    def get(self, request):
        student_family = StudentFamily.objects.filter(user=request.user)
        if student_family.exists():
            students = student_family[0].student_set.all()
            return render(request, 'student_app/profile.html', {'students': students, 'student_family': student_family[0]})
        else:
            return HttpResponseRedirect(reverse('registration:student_register'))
            # return render(request, 'student_app/profile.html')

