from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
import logging

from ..forms import SearchEmailForm, SearchNameForm, SearchPhoneForm
from ..models import StudentFamily, Student, User
logger = logging.getLogger(__name__)


class SearchView(LoginRequiredMixin, View):
    """Shows a message page"""
    def get(self, request):
        if not (request.user.is_board or request.user.is_superuser):
            return HttpResponseForbidden()
        email_form = SearchEmailForm()
        name_form = SearchNameForm()
        phone_form = SearchPhoneForm()
        return render(request, 'student_app/student_search.html',
                      {'email_form': email_form, 'name_form': name_form, 'phone_form': phone_form})

    def post(self, request):
        if not (request.user.is_board or request.user.is_superuser):
            return HttpResponseForbidden()
        if 'email' in request.POST:
            form = SearchEmailForm(request.POST)
            if form.is_valid():
                user = EmailAddress.objects.filter(email=form.cleaned_data['email'])
                if len(user) == 0:
                    return render(request, 'registration/message.html', {'message': 'No email found'})
                student_family = []
                for u in user:
                    student_family.append(StudentFamily.objects.filter(user=u.user))
                return render(request, 'student_app/search_result.html', {'student_family': student_family})
        elif 'first_name' in request.POST:
            form = SearchNameForm(request.POST)
            if form.is_valid():
                student = Student.objects.filter(first_name=form.cleaned_data['first_name'],
                                                 last_name=form.cleaned_data['last_name'])
                if len(student) == 0:
                    return render(request, 'registration/message.html', {'message': 'No student found'})
                student_family = []
                for s in student:
                    student_family.append(s.student_family)
                return render(request, 'student_app/search_result.html', {'student_family': student_family})
        elif 'phone' in request.POST:
            form = SearchPhoneForm(request.POST)
            if form.is_valid():
                s = StudentFamily.objects.filter(phone=form.cleaned_data['phone'])
                if len(s) == 0:
                    return render(request, 'registration/message.html', {'message': 'No student found'})
                return render(request, 'student_app/search_result.html', {'student_family': s})

        email_form = SearchEmailForm()
        name_form = SearchNameForm()
        phone_form = SearchPhoneForm()
        return render(request, 'student_app/student_search.html',
                      {'email_form': email_form, 'name_form': name_form, 'phone_form': phone_form})
