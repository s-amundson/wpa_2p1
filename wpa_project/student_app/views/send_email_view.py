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

#     def get(self, request, user_id=None):
#         if not request.user.is_board:
#             return Http404()
#         u = get_object_or_404(User, pk=user_id)
#         form = UserForm(instance=u)
#         return render(request, 'student_app/form_as_p.html', {'form': form})
#
#     def post(self, request, user_id=None):
#         if not request.user.is_board:
#             return Http404()
#         u = get_object_or_404(User, pk=user_id)
#         form = UserForm(request.POST, instance=u)
#         logging.debug(request.POST)
#         if form.is_valid():
#             f = form.save()
#         else:
#             logging.debug(form.errors)
#         return render(request, 'student_app/form_as_p.html', {'form': form})
