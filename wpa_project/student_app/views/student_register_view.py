from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
import logging

from ..models import StudentFamily
from ..forms import StudentRegistrationForm
logger = logging.getLogger(__name__)


class StudentRegisterView(LoginRequiredMixin, View):
    """To register a student"""
    def get(self, request):
        student_family = StudentFamily.objects.filter(user=request.user)
        if student_family.exists():
            form = StudentRegistrationForm(student_family)
            students = student_family.student
            logging.debug(students)
        else:
            form = StudentRegistrationForm()
            students = []
        logging.debug('here')
        return render(request, 'student_app/register.html', {'form': form, 'students': students})

