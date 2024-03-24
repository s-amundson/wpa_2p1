from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy

from ..forms import SendEmailForm
from ..tasks import send_email


class SendEmailView(UserPassesTestMixin, FormView):
    template_name = 'student_app/send_email.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('registration:index')
    is_super = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Send Email'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_super'] = self.is_super
        return kwargs

    def form_valid(self, form):
        send_email.delay(form.cleaned_data['recipients'], form.cleaned_data['subject'], form.cleaned_data['message'],
                         form.cleaned_data.get('include_days', None))
        return super().form_valid(form)

    def test_func(self):
        self.is_super = self.request.user.is_superuser
        return self.request.user.is_board
