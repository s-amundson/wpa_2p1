from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from django.http import Http404
import logging

from ..forms import SendEmailForm
from ..models import User


class SendEmailView(UserPassesTestMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('registration:index')
    is_super = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_super'] = self.is_super
        return kwargs

    def form_valid(self, form):
        form.send_message()
        return super().form_valid(form)

    def test_func(self):
        self.is_super = self.request.user.is_superuser
        return self.request.user.is_board
