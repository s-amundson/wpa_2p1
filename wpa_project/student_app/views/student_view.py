from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
import logging
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic import FormView

from ..forms import StudentDeleteForm, StudentForm
from ..models import Student
from ..src import EmailMessage, StudentHelper
from src.mixin import StudentFamilyMixin
logger = logging.getLogger(__name__)


class AddStudentView(UserPassesTestMixin, FormView):
    template_name = 'student_app/forms/student.html'
    form_class = StudentForm
    success_url = reverse_lazy('registration:profile')
    student = None

    def form_invalid(self, form):
        logging.warning(form.errors)
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            logging.debug('json error response')
            d = {'error': {}}
            for k,v in form.errors.items():
                d['error'][k] = v
            return JsonResponse(d)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.warning(form.cleaned_data)
        if self.request.user.is_board:
            f = form.save()
        else:
            f = form.save(commit=False)

            # student can't update thier own safety class. Fixes safety class date set to None student update.
            f.safety_class = form.initial.get('safety_class', None)

            if self.student:
                s = self.request.user.student_set.last()
                if s is None:  # pragma: no cover
                    logging.warning('Address required')
                    form.add_error(None, 'Address required')
                    return self.form_invalid(form)
                else:
                    # logging.debug(s.student_family.id)
                    f.student_family = s.student_family
                    self.request.session['student_family'] = s.student_family.id
            else:
                if self.request.user.student_set.first() is None:
                    f.user = self.request.user
                s = self.request.user.student_set.last()
                if s is not None:
                    f.student_family = s.student_family
            f.save()

            if f.user is None:
                if f.email is not None and f.email != self.request.user.email:
                    EmailMessage().invite_user_email(self.request.user.student_set.first(), f)
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            return JsonResponse({'id': f.id, 'first_name': form.cleaned_data['first_name'],
                                 'last_name': form.cleaned_data['last_name']})
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = kwargs.get('student', {})
        context['student']['is_user'] = 0
        context['student']['this_user'] = True
        student_id = self.kwargs.get('student_id', None)
        if student_id is not None:
            context['student']['id'] = student_id
            context['student']['is_joad'] = self.student.is_joad
            context['student']['is_user'] = self.student.user_id
            if self.request.user.is_staff:
                context['student']['this_user'] = False
            else:
                context['student']['this_user'] = (self.student.user == self.request.user)
            age = StudentHelper().calculate_age(self.student.dob)
            context['student']['joad_age'] = 8 < age < 21
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        student_id = self.kwargs.get('student_id', None)
        if student_id is not None:
            if self.request.user.is_staff:
                self.student = get_object_or_404(Student, pk=student_id)
            else:
                sf = self.request.user.student_set.last().student_family
                self.student = get_object_or_404(Student, id=student_id, student_family=sf)
        if self.student:
            kwargs['instance'] = self.student
        else:
            s = Student.objects.filter(user=self.request.user)
            if s.count() == 0:
                kwargs['initial'] = {'email': self.request.user.email}
        return kwargs

    def test_func(self):
        return self.request.user.is_authenticated


class StudentDeleteView(StudentFamilyMixin, FormView):
    template_name = 'student_app/delete.html'
    form_class = StudentDeleteForm
    success_url = reverse_lazy('registration:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Delete Student"
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(Student, pk=self.kwargs.get('pk'))
        if self.request.user.is_superuser or self.student_family == kwargs['instance'].student_family:
            return kwargs
        return self.handle_no_permission()

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        if form.cleaned_data['delete'].lower() == 'delete':
            student = Student.objects.get(pk=self.kwargs.get('pk'))
            student.delete()
        return super().form_valid(form)


class StudentIsJoadView(UserPassesTestMixin, View):
    def post(self, request, student_id):
        # logging.debug(request.POST)
        student = Student.objects.get(pk=student_id)
        age = StudentHelper().calculate_age(student.dob)
        if age < 9:
            return JsonResponse({'error': True, 'message': 'Student to young'})
        elif age > 20:
            return JsonResponse({'error': True, 'message': 'Student to old'})

        if f'joad_check_{student.id}' in request.POST:
            student.is_joad = request.POST[f'joad_check_{student.id}'].lower() in ['true', 'on']
            student.save()
            return JsonResponse({'error': False, 'message': ''})
        return JsonResponse({'error': True, 'message': ''})

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False
