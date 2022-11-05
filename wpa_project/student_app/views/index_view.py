from django.shortcuts import reverse
from facebook.views import PostList
from allauth.account.forms import LoginForm

import logging
logger = logging.getLogger(__name__)


class IndexView(PostList):
    template_name = 'student_app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        context['signup_url'] = reverse('account_signup')
        return context
