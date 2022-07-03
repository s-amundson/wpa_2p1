from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
import logging
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
from django.views.generic import FormView
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

from ..forms import StudentForm
from ..models import Student
from ..serializers import StudentSerializer
from ..src import EmailMessage, StudentHelper
logger = logging.getLogger(__name__)


class StudentApiView(LoginRequiredMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id=None, format=None):
        if student_id is not None:
            student = get_object_or_404(Student, pk=student_id)
            # students = StudentFamily.objects.get(user=request.user).student_set.all()
            if request.user.is_staff or student_id == request.user.id:
                serializer = StudentSerializer(student)
            else:
                return Response({'error': "Not Authorized"}, status=400)
        else:
            serializer = StudentSerializer()
        return Response(serializer.data)

    def post(self, request, student_id=None, format=None):
        # logging.debug(student_id)
        logging.debug(request.data)
        old_email = None
        if student_id is not None:
            if request.user.is_staff:
                student = get_object_or_404(Student, id=student_id)
            else:
                sf = get_object_or_404(Student, user=request.user).student_family
                student = get_object_or_404(Student, id=student_id, student_family=sf)
                old_email = student.email
            serializer = StudentSerializer(student, data=request.data)

        else:
            serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            logging.debug(serializer.validated_data)
            if student_id is None:
                owner = Student.objects.filter(user=request.user)
                if owner.count() == 0:
                    logging.debug('student is user')
                    f = serializer.save(user=request.user)
                else:
                    f = serializer.save(student_family=owner[0].student_family)

            else:
                f = serializer.update(student, serializer.validated_data)

            if f.user is None:
                logging.debug('student is not user')
                if f.email != old_email:
                    logging.debug('email updated')
                    EmailMessage().invite_user_email(request.user, f)
            # request.session['student_family'] = f.student_family.id
            # logging.debug(f'id = {f.id}, fam = {f.student_family.id}')
            return Response(serializer.data)
        logging.debug(serializer.errors)
        return Response({'error': serializer.errors})


class AddStudentView(LoginRequiredMixin, FormView):
    template_name = 'student_app/forms/student.html'
    form_class = StudentForm
    success_url = reverse_lazy('registration:profile')
    student = None

    def form_invalid(self, form):
        logging.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logging.debug(form.cleaned_data)
        if self.request.user.is_board:
            form.save()
        else:
            f = form.save(commit=False)
            sf = Student.objects.get(user=self.request.user).student_family
            logging.debug(sf.id)
            f.student_family = sf
            self.request.session['student_family'] = sf.id
            f.save()
        if self.request.META.get('HTTP_ACCEPT', '').find('application/json') >= 0:
            return JsonResponse({'id': 1, 'first_name': form.cleaned_data['first_name'],
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
        logging.debug(context)
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
        logging.debug(kwargs)
        return kwargs


class StudentIsJoadView(UserPassesTestMixin, View):
    def post(self, request, student_id):
        logging.debug(request.POST)
        student = Student.objects.get(pk=student_id)
        age = StudentHelper().calculate_age(student.dob)
        logging.debug(age)
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
