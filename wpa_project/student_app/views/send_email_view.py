from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from django.http import Http404
import logging

from ..forms import UserForm
from ..models import User


class SendEmailView(LoginRequiredMixin, View):
    def get(self, request, user_id=None):
        if not request.user.is_board:
            return Http404()
        u = get_object_or_404(User, pk=user_id)
        form = UserForm(instance=u)
        return render(request, 'student_app/form_as_p.html', {'form': form})

    def post(self, request, user_id=None):
        if not request.user.is_board:
            return Http404()
        u = get_object_or_404(User, pk=user_id)
        form = UserForm(request.POST, instance=u)
        logging.debug(request.POST)
        if form.is_valid():
            f = form.save()
        else:
            logging.debug(form.errors)
        return render(request, 'student_app/form_as_p.html', {'form': form})
