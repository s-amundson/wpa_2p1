from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse

from ..models import Student, StudentFamily
from ..forms import StudentDeleteForm, StudentFamilyRegistrationForm
from src.mixin import StudentFamilyMixin

import logging
logger = logging.getLogger(__name__)


class StudentFamilyView(LoginRequiredMixin, FormView):
    template_name = 'student_app/forms/student_family_form.html'
    form_class = StudentFamilyRegistrationForm
    student_family = None
    success_url = reverse_lazy('registration:profile')

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        f = form.save()
        s = self.request.user.student_set.last()
        if s.student_family is None:
            # logging.debug(f)
            s.student_family = f
            s.save()

        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            d = form.cleaned_data
            d['id'] = f.id
            return JsonResponse(d)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
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
                if self.student_family and self.student_family.id != family_id:
                    raise Http404("Authorization Error.")
        if self.student_family is not None:
            kwargs['instance'] = self.student_family
        return kwargs


class StudentFamilyDeleteView(StudentFamilyMixin, FormView):
    template_name = 'student_app/delete.html'
    form_class = StudentDeleteForm
    success_url = reverse_lazy('registration:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Delete Account"
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(StudentFamily, pk=self.kwargs.get('pk'))
        kwargs['delete_family'] = True
        if self.request.user.is_superuser:
            self.student_family = kwargs['instance']
            return kwargs
        if self.student_family == kwargs['instance']:
            return kwargs
        return self.handle_no_permission()

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        logger.warning(self.student_family)
        for student in self.student_family.student_set.filter(user__isnull=False):
            student.user.delete()
        self.student_family.student_set.all().delete()
        self.student_family.delete()
        return super().form_valid(form)
