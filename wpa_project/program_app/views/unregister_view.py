from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from ..forms import UnregisterForm
from student_app.models import StudentFamily
import logging
logger = logging.getLogger(__name__)


class UnregisterView(UserPassesTestMixin, FormView):
    template_name = 'program_app/unregister.html'
    form_class = UnregisterForm
    success_url = reverse_lazy('programs:class_registration')
    student_family = None

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # logging.debug(form.cleaned_data)
        if form.process_refund(self.request.user, self.student_family):
            return super().form_valid(form)
        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['family'] = self.student_family
        # if self.request.user.is_board:
        #     kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.student_set.last() is not None:
            self.student_family = self.request.user.student_set.first().student_family
            if self.request.user.is_board and self.kwargs.get('family_id'):
                self.student_family = get_object_or_404(StudentFamily, pk=self.kwargs.get('family_id'))
        return self.student_family is not None


class UnregisterTableView(UnregisterView):
    template_name = 'program_app/forms/unregister.html'
