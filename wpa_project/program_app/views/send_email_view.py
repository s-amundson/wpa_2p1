from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
import logging

from ..forms import SendClassEmailForm
from ..models import BeginnerClass


class SendEmailView(UserPassesTestMixin, FormView):
    beginner_class = None
    template_name = 'student_app/form_as_p.html'
    form_class = SendClassEmailForm
    success_url = reverse_lazy('registration:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['beginner_class'] = self.beginner_class
        return kwargs

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # logging.debug(form.cleaned_data)
        form.send_message()
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_authenticated:
            bid = self.kwargs.get('beginner_class', None)
            if bid is not None:
                self.beginner_class = get_object_or_404(BeginnerClass, pk=bid)
                self.success_url = reverse_lazy('events:event_attend_list', kwargs={'event': self.beginner_class.event.id})
                return self.request.user.has_perm('student_app.board')
        return False
