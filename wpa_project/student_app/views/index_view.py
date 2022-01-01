from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from django.contrib import messages


class IndexView(View):
    """Shows a message page"""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('programs:class_registration'))
        return render(request, 'student_app/index.html')
