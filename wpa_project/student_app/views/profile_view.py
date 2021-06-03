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
        logging.debug(request.user.email)
        logging.debug(f'user is staff = {request.user.is_staff}')
        logging.debug(student_family.exists())
        if student_family.exists():
            logging.debug(student_family[0])
            students = student_family[0].student_set.all()
            logging.debug(students)
            return render(request, 'student_app/profile.html', {'students': students, 'student_family': student_family[0]})
        else:
            return HttpResponseRedirect(reverse('registration:student_register'))
            # return render(request, 'student_app/profile.html')

