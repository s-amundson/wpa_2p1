from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import FormView

import logging
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.views.generic.base import View

from ..forms import InstructorForm
logger = logging.getLogger(__name__)


class InstructorUpdateView(UserPassesTestMixin, FormView):
    form_class = InstructorForm
    template_name = 'student_app/forms/instructor.html'

    def form_invalid(self, form):
        logging.warning(form.errors)
        return JsonResponse({'status': "error"})

    def form_valid(self, form):
        self.request.user.instructor_expire_date = form.cleaned_data.get('instructor_expire_date',
                                                                         self.request.user.instructor_expire_date)
        self.request.user.instructor_level = form.cleaned_data.get('instructor_level',
                                                                   self.request.user.instructor_level)
        self.request.user.save()
        return JsonResponse({
            'status': 'SUCCESS',
            'expire_date': self.request.user.instructor_expire_date,
            'level': self.request.user.instructor_level
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_instructor
        return False  # pragma: no cover
