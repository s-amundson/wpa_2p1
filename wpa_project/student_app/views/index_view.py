from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from django.contrib import messages
from facebook.views import PostList
from allauth.account.forms import LoginForm

import logging
logger = logging.getLogger(__name__)

class IndexView(PostList):
    template_name = 'student_app/index.html'

    def get_context_data(self, **kwargs):
        # self.request.session.pop('theme')
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        context['signup_url'] = reverse('account_signup')
        logging.warning(self.request.session.get('theme', ''))
        return context
    # """Shows a message page"""
    # def get(self, request):
    #     if request.user.is_authenticated:
    #         return redirect(reverse('programs:class_registration'))
    #     return render(request, 'student_app/index.html')
