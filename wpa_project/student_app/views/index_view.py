from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from django.contrib import messages
from facebook.views import PostList
from allauth.account.forms import LoginForm


class IndexView(PostList):
    template_name = 'student_app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context
    # """Shows a message page"""
    # def get(self, request):
    #     if request.user.is_authenticated:
    #         return redirect(reverse('programs:class_registration'))
    #     return render(request, 'student_app/index.html')
