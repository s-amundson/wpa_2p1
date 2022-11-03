from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import JsonResponse

from ..forms import ThemeForm

import logging
logger = logging.getLogger(__name__)


class ThemeView(FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = ThemeForm
    success_url = reverse_lazy('registration:profile')

    def form_invalid(self, form):
        logging.warning(form.errors)
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            return JsonResponse({'status': 'error'})
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.warning(form.cleaned_data)
        self.request.session['theme'] = form.cleaned_data.get('theme', 'browser')
        if self.request.user.is_authenticated:
            self.request.user.theme = form.cleaned_data.get('theme', 'browser')
            self.request.user.save()
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            return JsonResponse({'status': 'success'})
        return super().form_valid(form)
