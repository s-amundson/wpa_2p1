from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views.generic.base import View
import logging

from ..forms import SearchEmailForm, SearchNameForm, SearchPhoneForm
from ..models import StudentFamily, Student
logger = logging.getLogger(__name__)


class SearchResultView(UserPassesTestMixin, View):
    def get(self, request, student_family):
        s = StudentFamily.objects.filter(pk=student_family)
        return render(request, 'student_app/search_result.html', {'student_family': s})

    def test_func(self):
        return self.request.user.is_board

class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        if not (request.user.is_board or request.user.is_staff):
            return HttpResponseForbidden()
        email_form = SearchEmailForm()
        name_form = SearchNameForm()
        phone_form = SearchPhoneForm()
        return render(request, 'student_app/student_search.html',
                      {'email_form': email_form, 'name_form': name_form, 'phone_form': phone_form})

    def post(self, request):
        if not (request.user.is_board or request.user.is_staff):
            return HttpResponseForbidden()
        if 'email' in request.POST:
            form = SearchEmailForm(request.POST)
            if form.is_valid():
                user = EmailAddress.objects.filter(email__iexact=form.cleaned_data['email'])
                if len(user) == 0:
                    return render(request, 'student_app/message.html', {'message': 'No email found'})
                student_family = []
                for u in user:
                    # student_family.append(StudentFamily.objects.get(user__id=u.user_id))
                    try:
                        student = Student.objects.get(user__id=u.user_id)
                    except Student.DoesNotExist:
                        return render(request, 'student_app/message.html', {'message': 'No student found'})
                    # logging.debug(student)
                    student_family.append(student.student_family)
                return render(request, 'student_app/search_result.html', {'student_family': student_family})
        elif 'first_name' in request.POST:
            form = SearchNameForm(request.POST)
            if form.is_valid():
                student = Student.objects.filter(first_name__iexact=form.cleaned_data['first_name'],
                                                 last_name__iexact=form.cleaned_data['last_name'])
                if len(student) == 0:
                    return render(request, 'student_app/message.html', {'message': 'No student found'})
                student_family = []
                for s in student:
                    student_family.append(s.student_family)
                return render(request, 'student_app/search_result.html', {'student_family': student_family})
        elif 'phone' in request.POST:
            form = SearchPhoneForm(request.POST)
            if form.is_valid():
                s = StudentFamily.objects.filter(phone=form.cleaned_data['phone'])
                if len(s) == 0:
                    return render(request, 'student_app/message.html', {'message': 'No student found'})
                return render(request, 'student_app/search_result.html', {'student_family': s})

        email_form = SearchEmailForm()
        name_form = SearchNameForm()
        phone_form = SearchPhoneForm()
        return render(request, 'student_app/student_search.html',
                      {'email_form': email_form, 'name_form': name_form, 'phone_form': phone_form})

