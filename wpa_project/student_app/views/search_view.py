from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
import logging

from ..forms import SearchEmailForm, SearchNameForm, SearchPhoneForm
from ..models import StudentFamily, Student
logger = logging.getLogger(__name__)


class SearchView(LoginRequiredMixin, View):
    """Shows a message page"""
    def get(self, request):
        if not request.user.is_board:
            return HttpResponseForbidden()
        email_form = SearchEmailForm()
        name_form = SearchNameForm()
        phone_form = SearchPhoneForm()
        return render(request, 'student_app/student_search.html',
                      {'email_form': email_form, 'name_form': name_form, 'phone_form': phone_form})

