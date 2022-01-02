from django.shortcuts import render
from django.views.generic.base import View
from django.conf import settings


class HelpView(View):
    def get(self, request):

        return render(request, 'student_app/help.html', {'email': settings.DEFAULT_FROM_EMAIL})

