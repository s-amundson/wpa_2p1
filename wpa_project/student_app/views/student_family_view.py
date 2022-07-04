from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse

from ..models import Student, StudentFamily
from ..forms import StudentFamilyRegistrationForm

import logging
logger = logging.getLogger(__name__)


class StudentFamilyView(LoginRequiredMixin, FormView):
    template_name = 'student_app/forms/student_family_form.html'
    form_class = StudentFamilyRegistrationForm
    student_family = None
    success_url = reverse_lazy('registration:profile')

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        f = form.save()
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            d = form.cleaned_data
            d['id'] = f.id
            return JsonResponse(d)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        logging.debug(kwargs)
        family_id = self.kwargs.get('family_id', None)
        if family_id is None:
            student = Student.objects.filter(user=self.request.user).last()
            if student is not None:
                self.student_family = student.student_family
        else:
            if self.request.user.is_staff:
                self.student_family = get_object_or_404(StudentFamily, pk=family_id)
            else:
                self.student_family = get_object_or_404(Student, user=self.request.user).student_family
                if self.student_family.id != family_id:
                    raise Http404("Authorization Error.")
        if self.student_family is not None:
            kwargs['instance'] = self.student_family
        return kwargs

