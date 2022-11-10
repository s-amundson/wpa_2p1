from allauth.account.views import SignupView as ASV
from ipware import get_client_ip

import logging
logger = logging.getLogger(__name__)


class SignupView(ASV):
    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        scores = self.request.session.get('recaptcha_scores', [])
        if len(scores):
            average = sum(scores) / len(scores)
        else:
            average = 0
        logging.warning(average)
        return dispatch

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['client_ip'], kwargs['is_routable'] = get_client_ip(self.request)
        logging.warning(f"ip: {kwargs['client_ip']}, routable: {kwargs['is_routable']}")
        return kwargs
