from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404

import logging

from ..forms import UserForm
from ..models import User


class UserView(UserPassesTestMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = UserForm
    success_url = reverse_lazy('registration:profile')
    user = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.user
        return kwargs

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        form.save()
        logging.debug('valid')
        return super().form_valid(form)

    def test_func(self):
        uid = self.kwargs.get('user_id', None)
        if uid is not None:
            self.user = get_object_or_404(User, pk=uid)
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False
