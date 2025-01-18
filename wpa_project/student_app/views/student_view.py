from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
import logging
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
from django.views.generic import FormView

from ..forms import StudentDeleteForm, StudentForm
from ..models import Student
from ..src import EmailMessage, StudentHelper
from src.mixin import StaffMixin, StudentFamilyMixin
logger = logging.getLogger(__name__)


class AddStudentView(UserPassesTestMixin, FormView):
    template_name = 'student_app/forms/student.html'
    form_class = StudentForm
    success_url = reverse_lazy('registration:profile')
    student = None

    def form_invalid(self, form):
        logger.warning(form.errors)
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            logger.debug('json error response')
            d = {'error': {}}
            for k,v in form.errors.items():
                d['error'][k] = v
            return JsonResponse(d)
        return super().form_invalid(form)

    def form_valid(self, form):
        # logger.warning(form.cleaned_data)
        if self.request.user.is_board:
            f = form.save()
        else:
            f = form.save(commit=False)

            # student can't update their own safety class. Fixes safety class date set to None student update.
            f.safety_class = form.initial.get('safety_class', None)

            if self.student:
                s = self.request.user.student_set.last()
                if s is None:  # pragma: no cover
                    logger.warning('Address required')
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
        context['student']['staff'] = False
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
            if self.student.user is not None and self.student.user.is_staff:
                context['student']['staff'] = True
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
    student = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:  # pragma: no cover
            return self.handle_no_permission()
        if request.user.student_set.last() is None or request.user.student_set.last().student_family is None:  # pragma: no cover
            request.session['message'] = 'Address form is required'
            return HttpResponseRedirect(reverse('registration:profile'))
        self.student_family = request.user.student_set.last().student_family
        self.student = get_object_or_404(Student, pk=self.kwargs.get('pk'))
        if self.request.user.is_superuser or self.student_family == self.student.student_family:
            if self.request.user.is_superuser:
                self.student_family = self.student.student_family
            logger.warning(self.student_family.student_set.filter(user__isnull=False).count())
            # prevent dangling students
            if self.student_family.student_set.filter(user__isnull=False).count() > 1 or not self.student.user:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse('registration:delete_student_family',
                                                    kwargs={'pk': self.student_family.id}))
        return self.handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Delete Student"
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.student
        return kwargs

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        student = Student.objects.get(pk=self.kwargs.get('pk'))
        if student.user:
            if form.cleaned_data['removal_choice'] == 'delete':
                student.user.delete()
                student.delete()
            else:
                student.student_family = None
                student.save()
        else:
            student.delete()
        return super().form_valid(form)


class StudentIsJoadView(StaffMixin, View):
    def post(self, request, student_id):
        # logging.debug(request.POST)
        student = Student.objects.get(pk=student_id)
        if student.user is not None and student.user.is_staff:
            pass
        else:
            age = StudentHelper().calculate_age(student.dob)
            if age < 9:
                return JsonResponse({'error': True, 'message': 'Student to young'})
            elif age > 20:
                return JsonResponse({'error': True, 'message': 'Student to old'})

        if f'joad_check_{student.id}' in request.POST:
            student.is_joad = request.POST[f'joad_check_{student.id}'].lower() in ['true', 'on']
            student.save()
            return JsonResponse({'error': False, 'message': ''})
        return JsonResponse({'error': True, 'message': ''})  # pragma: no cover
