from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging

from ..models import StudentFamily
from ..forms import StudentFamilyRegistrationForm
logger = logging.getLogger(__name__)


class StudentFamilyRegisterView(LoginRequiredMixin, View):
    """To register a student"""

    def get_students(self, request, family_id):
        if family_id is None:
            student_family = StudentFamily.objects.filter(user=request.user)
            if student_family.exists():
                self.form = StudentFamilyRegistrationForm(instance=student_family[0])
            else:
                self.form = StudentFamilyRegistrationForm()
        else:
            student_family = get_object_or_404(StudentFamily, pk=family_id)
            self.form = StudentFamilyRegistrationForm(instance=student_family)

    def get(self, request, family_id=None):

        self.get_students(request, family_id)
        message = request.session.get('message', '')
        logging.debug(message)
        return render(request, 'student_app/forms/student_family_form.html', {'form': self.form, 'message': message})

    def post(self, request, family_id=None):
        form = StudentFamilyRegistrationForm(request.POST)
        if form.is_valid():

            f = form.save()
            f.user.add(request.user)
            # request.session['student_family'] = f.id
            logging.debug(f'id = {f.id}, user = {f.user}')
            return HttpResponseRedirect(reverse('registration:profile'))
        else:
            logging.debug(form.errors)
        self.get_students(request, family_id)
        return render(request, 'student_app/register.html', {'form': form})

