from allauth.account.views import SignupView as ASV
from ipware import get_client_ip

import logging
logger = logging.getLogger(__name__)


class SignupView(ASV):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        score = self.request.session.get('recaptcha_score', 0)
        logger.warning(score)
        context['probably_human'] = score > 0.5
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['client_ip'], kwargs['is_routable'] = get_client_ip(self.request)
        logger.warning(f"ip: {kwargs['client_ip']}, routable: {kwargs['is_routable']}")
        return kwargs

    def form_valid(self, form):
        if self.request.session.get('recaptcha_score', 0) > 0.5:
            return super().form_valid(form)
        else:
            form.add_error(None, 'In order to prevent spam accounts we are unable to process this request at this time.')
            return self.form_invalid(form)
