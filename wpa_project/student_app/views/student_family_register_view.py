from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging

from ..models import StudentFamily
from ..forms import StudentFamilyRegistrationForm
logger = logging.getLogger(__name__)


class StudentFamilyRegisterView(LoginRequiredMixin, View):
    """To register a student"""

    def get_students(self, request):
        student_family = StudentFamily.objects.filter(user=request.user)
        if student_family.exists():
            self.form = StudentFamilyRegistrationForm(instance=student_family[0])
        else:
            self.form = StudentFamilyRegistrationForm()

    def get(self, request):
        logging.debug(request)
        self.get_students(request)
        logging.debug('here')
        return render(request, 'student_app/register.html', {'form': self.form})

    def post(self, request):
        form = StudentFamilyRegistrationForm(request.POST)
        logging.debug(request.POST)
        if form.is_valid():
            logging.debug(form.cleaned_data)
            f = form.save()
            f.user.add(request.user)
            # request.session['student_family'] = f.id
            logging.debug(f'id = {f.id}, user = {f.user}')
            return HttpResponseRedirect(reverse('registration:profile'))
        else:
            logging.debug(form.errors)
        self.get_students(request)
        return render(request, 'student_app/register.html', {'form': form})

