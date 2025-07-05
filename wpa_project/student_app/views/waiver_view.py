from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from csp.decorators import csp_update

from student_app.forms import WaiverForm
from student_app.models import Student
from ..tasks import waiver_pdf

import logging
logger = logging.getLogger(__name__)


class WaiverView(UserPassesTestMixin, FormView):
    template_name = 'program_app/class_sign_in.html'
    form_class = WaiverForm
    success_url = reverse_lazy('registration:profile')
    form = None
    student = None
    class_date = None

    @csp_update({"style-src": ["https://ajax.googleapis.com"], "script-src": ["https://ajax.googleapis.com"]})
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = self.student
        context['awrl'] = get_template('program_app/awrl.txt').render()
        return context

    def get_form(self):
        return self.form_class(self.student, **self.get_form_kwargs())

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # self.form = form
        if form.check_signature(self.class_date):
            self.update_attendance()
            waiver_pdf.delay(self.student.id, form.cleaned_data['sig_first_name'], form.cleaned_data['sig_last_name'])
            # form.send_pdf()
            return HttpResponseRedirect(self.success_url)
        return self.form_invalid(form)

    def test_func(self):
        sid = self.kwargs.get('student_id', None)
        if sid is not None:
            self.student = get_object_or_404(Student, pk=sid)
        return self.request.user.has_perm('student_app.staff')

    def update_attendance(self):
        pass


class WaiverRecreateView(WaiverView):  # pragma: no cover
    def get(self, request, *args, **kwargs):
        waiver_pdf.delay(self.student.id, self.student.first_name, self.student.last_name)
        return HttpResponseRedirect(self.success_url)

    def test_func(self):
        sid = self.kwargs.get('student_id', None)
        if sid is not None:
            self.student = get_object_or_404(Student, pk=sid)
        if self.request.user.is_authenticated:
            return self.request.user.is_superuser
        else:
            return False