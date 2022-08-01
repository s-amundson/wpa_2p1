from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
import logging

from ..forms import SearchEmailForm, SearchNameForm, SearchPhoneForm
from ..models import StudentFamily, Student
from program_app.src import ClassRegistrationHelper
from program_app.forms import UnregisterForm
logger = logging.getLogger(__name__)


class SearchResultListView(UserPassesTestMixin, ListView):
    families = []
    model = StudentFamily
    template_name = 'student_app/search_result_list.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['families'] = self.families
        logging.debug(context)
        return context

    def get_queryset(self):
        self.queryset = self.families

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            if self.request.session.get('families', None) is not None:
                self.families = StudentFamily.objects.filter(id__in=self.request.session.pop('families'))
            return True
        return False


class SearchResultView(UserPassesTestMixin, TemplateView):
    template_name = 'student_app/search_result.html'
    student_family = None
    student_family_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attend_history'] = ClassRegistrationHelper().attendance_history_queryset(self.student_family)
        context['student_family'] = self.student_family
        context['form'] = UnregisterForm(family=self.student_family)
        logging.debug(context['student_family'])
        return context

    # def get(self, request, student_family):
    #     s = StudentFamily.objects.filter(pk=student_family)
    #     logging.debug(s)
    #     return render(request, 'student_app/search_result.html', {'student_family': s})

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            self.student_family_id = self.kwargs.get('student_family', None)
            self.student_family = get_object_or_404(StudentFamily, pk=self.student_family_id)
            return self.student_family_id is not None
        return False


class SearchAbstractView(UserPassesTestMixin, FormView):
    template_name = 'student_app/student_search.html'
    success_url = reverse_lazy('registration:search_result_list')
    form_class = SearchEmailForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_form'] = SearchEmailForm()
        context['name_form'] = SearchNameForm()
        context['phone_form'] = SearchPhoneForm()
        return context

    def form_invalid(self, form):
        logging.debug(form.errors)
        return super().form_invalid(form)

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class SearchEmailView(SearchAbstractView):
    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        emails = EmailAddress.objects.filter(email__iexact=form.cleaned_data['email'])
        if len(emails) == 0:
            form.add_error('email', 'Not Found')
            messages.add_message(self.request, messages.ERROR, 'no students found')
            return self.form_invalid(form)
        fam_list = []
        for email in emails:
            try:
                student = Student.objects.get(user=email.user)
                fam_list.append(student.student_family.id)
            except Student.DoesNotExist:  # pragma: no cover
                pass
        logging.debug(fam_list)
        self.request.session['families'] = fam_list
        return super().form_valid(form)


class SearchNameView(SearchAbstractView):
    form_class = SearchNameForm

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        student = Student.objects.filter(first_name__iexact=form.cleaned_data['first_name'],
                                         last_name__iexact=form.cleaned_data['last_name'])
        if len(student) == 0:
            form.add_error('last_name', 'Not Found')
            messages.add_message(self.request, messages.ERROR, 'no students found')
            return self.form_invalid(form)

        student_family = []
        for s in student:
            student_family.append(s.student_family.id)
        logging.debug(student_family)
        self.request.session['families'] = student_family
        return super().form_valid(form)


class SearchPhoneView(SearchAbstractView):
    form_class = SearchPhoneForm

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        phone = form.cleaned_data['phone'].replace('-', '').replace('.', '')
        if len(phone) < 10:
            form.add_error('phone', 'Invalid phone number')
            messages.add_message(self.request, messages.ERROR, 'invalid phone number')
            return self.form_invalid(form)
        sf = StudentFamily.objects.filter(phone__icontains=phone)
        if len(sf) == 0:
            form.add_error('phone', 'Not Found')
            messages.add_message(self.request, messages.ERROR, 'no students found')
            return self.form_invalid(form)
        fam_list = []
        for s in sf:
            fam_list.append(s.id)
        self.request.session['families'] = fam_list
        return super().form_valid(form)
