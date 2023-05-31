from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import JsonResponse
from ipware import get_client_ip

from ..forms import RecaptchaForm

import logging
logger = logging.getLogger(__name__)


class RecaptchaView(FormView): # pragma: no cover
    template_name = 'student_app/form_as_p.html'
    form_class = RecaptchaForm
    success_url = reverse_lazy('registration:profile')

    def form_invalid(self, form):
        logger.warning(self.request.POST)
        logger.warning(form.errors)
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            return JsonResponse({'status': 'error'})
        return super().form_invalid(form)

    def form_valid(self, form):
        client_ip, is_routable = get_client_ip(self.request)
        score = form.get_score(client_ip)
        if score is not None:
            self.request.session['recaptcha_score'] = score
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            # logging.warning('json response')
            return JsonResponse({'status': 'success'})
        self.success_url = form.cleaned_data['url']
        return super().form_valid(form)
