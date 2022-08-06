from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse_lazy

from ..forms import ThemeForm

import logging
logger = logging.getLogger(__name__)


class ThemeView(LoginRequiredMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = ThemeForm
    success_url = reverse_lazy('registration:profile')

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.request.user.dark_theme = form.cleaned_data.get('theme', 'light') == 'dark'
        self.request.user.save()
        return super().form_valid(form)
