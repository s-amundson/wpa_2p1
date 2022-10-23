from allauth.account.views import SignupView as ASV
from ipware import get_client_ip

import logging
logger = logging.getLogger(__name__)


class SignupView(ASV):
    template_name = 'account/login_insert.html'
    # client_ip = None
    # is_routable = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['client_ip'], kwargs['is_routable'] = get_client_ip(self.request)
        logging.warning(f"ip: {kwargs['client_ip']}, routable: {kwargs['is_routable']}")
        return kwargs
