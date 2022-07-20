from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
import logging
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic import FormView

from ..forms import StudentForm
from ..models import Student
from ..src import EmailMessage, StudentHelper
logger = logging.getLogger(__name__)


class AddStudentView(LoginRequiredMixin, FormView):
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
        logging.debug(form.cleaned_data)
        if self.request.user.is_board:
            f = form.save()
        else:
            f = form.save(commit=False)
            logging.debug(self.student)
            if self.student:
                logging.debug('is student')
                s = self.request.user.student_set.last()
                if s is not None:
                    logging.debug(s.student_family.id)
                    f.student_family = s.student_family
                    self.request.session['student_family'] = s.student_family.id
            else:
                logging.debug('here')
                if self.request.user.student_set.first() is None:
                    logging.debug('user is student')
                    f.user = self.request.user
                s = self.request.user.student_set.last()
                if s is not None:
                    logging.debug(s.student_family.id)
                    f.student_family = s.student_family
            f.save()

            if f.user is None:
                if f.email is not None and f.email != self.request.user.email:
                    logging.debug('invite')
                    EmailMessage().invite_user_email(self.request.user.student_set.first(), f)
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            logging.debug('json response')
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
            if self.request.user.is_staff:
                context['student']['is_joad'] = self.student.is_joad
                context['student']['is_user'] = self.student.user_id
                context['student']['this_user'] = False
            else:
                logging.debug(self.student.user)
                context['student']['is_user'] = self.student.user_id
                context['student']['is_joad'] = self.student.is_joad
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
                sf = Student.objects.get(user=self.request.user).student_family
                self.student = get_object_or_404(Student, id=student_id, student_family=sf)
        if self.student:
            kwargs['instance'] = self.student
            kwargs['student_is_user'] = self.student.user_id
        else:
            s = Student.objects.filter(user=self.request.user)
            if s.count() == 0:
                kwargs['initial'] = {'email': self.request.user.email}
        return kwargs


class StudentIsJoadView(UserPassesTestMixin, View):
    def post(self, request, student_id):
        logging.debug(request.POST)
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
