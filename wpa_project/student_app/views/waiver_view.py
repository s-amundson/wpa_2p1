from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404

from student_app.forms import WaiverForm
from student_app.models import Student

import logging
logger = logging.getLogger(__name__)


class WaiverView(UserPassesTestMixin, FormView):
    template_name = 'program_app/class_sign_in.html'
    form_class = WaiverForm
    success_url = reverse_lazy('registration:profile')
    form = None
    student = None
    class_date = timezone.localtime(timezone.now()).date()

    def get_form(self):
        return self.form_class(self.student, **self.get_form_kwargs())

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.form = form
        # logging.debug('valid')
        # logging.debug(self.class_date)
        if form.make_pdf(self.class_date):
            self.update_attendance()
            form.send_pdf()
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        # logging.debug(self.request.POST)
        return super().post(request, *args, **kwargs)

    def test_func(self):
        sid = self.kwargs.get('student_id', None)
        if sid is not None:
            self.student = get_object_or_404(Student, pk=sid)
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False

    def update_attendance(self):
        pass

