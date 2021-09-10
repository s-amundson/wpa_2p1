from django.shortcuts import render
from django.views.generic.base import View
from django.contrib import messages

class IndexView(View):
    """Shows a message page"""
    def get(self, request):
        return render(request, 'student_app/index.html')
