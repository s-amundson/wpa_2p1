from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from django.views.generic.base import View
import logging

from ..models import Student, StudentFamily
from ..forms import StudentFamilyRegistrationForm
logger = logging.getLogger(__name__)


class StudentFamilyRegisterView(LoginRequiredMixin, View):
    """To register a student"""

    def get(self, request, family_id=None):
        # logging.debug('here')
        if family_id is None:
            try:
                student_family = Student.objects.get(user=request.user).student_family
                form = StudentFamilyRegistrationForm(instance=student_family)
            except Student.DoesNotExist:  # pragma: no cover
                form = StudentFamilyRegistrationForm()
        else:
            if request.user.is_staff:
                student_family = get_object_or_404(StudentFamily, pk=family_id)
            else:
                # student_family = get_object_or_404(StudentFamily, pk=family_id, user=request.user)
                student_family = get_object_or_404(Student, user=request.user).student_family
                if student_family.id != family_id:
                    raise Http404("No MyModel matches the given query.")
            form = StudentFamilyRegistrationForm(instance=student_family)
        message = request.session.get('message', '')
        logging.debug(message)
        return render(request, 'student_app/forms/student_family_form.html', {'form': form, 'message': message})
