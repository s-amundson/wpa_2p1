from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import logging

from ..forms import StudentForm
from ..models import Student
logger = logging.getLogger(__name__)


class AddStudentView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'student_app/student.html'
    form_class = StudentForm
    success_message = 'Success: Student was added'
    success_url = reverse_lazy('registration:profile')

