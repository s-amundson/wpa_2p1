from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from ..forms import AdmitWaitForm
from ..models import BeginnerClass
from student_app.models import StudentFamily
import logging
logger = logging.getLogger(__name__)


class AdmitWaitView(UserPassesTestMixin, FormView):
    beginner_class = None
    template_name = 'program_app/admit_wait.html'
    form_class = AdmitWaitForm
    success_url = reverse_lazy('programs:class_list')
    student_family = None

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        if form.process_admission():
            return super().form_valid(form)
        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['beginner_class'] = self.beginner_class
        kwargs['family'] = self.student_family
        return kwargs

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            if self.kwargs.get('beginner_class'):
                self.beginner_class = get_object_or_404(BeginnerClass, pk=self.kwargs.get('beginner_class'))
                self.success_url = reverse_lazy('programs:class_attend_list',
                                                kwargs={'event': self.beginner_class.event.id})
            if self.kwargs.get('family_id'):
                self.student_family = get_object_or_404(StudentFamily, pk=self.kwargs.get('family_id'))
        return self.beginner_class is not None
