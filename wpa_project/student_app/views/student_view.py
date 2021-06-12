from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
import logging
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic.base import View
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

from ..forms import StudentForm
from ..models import Student, StudentFamily
from ..serializers import StudentSerializer

logger = logging.getLogger(__name__)


class StudentApiView(LoginRequiredMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id=None, format=None):
        if student_id is not None:
            student = get_object_or_404(Student, pk=student_id)
            serializer = StudentSerializer(student)
        else:
            serializer = StudentSerializer()
        return Response(serializer.data)

    def post(self, request, student_id=None, format=None):
        logging.debug(student_id)
        logging.debug(request.data)
        if student_id is not None:
            try:
                student = Student.objects.get(pk=student_id)
                serializer = StudentSerializer(student, data=request.data)
            except Student.DoesNotExist:
                raise Http404
        else:
            serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            logging.debug(serializer.validated_data)
            if student_id is None:
                sf = get_object_or_404(StudentFamily, user=request.user)
                f = serializer.save(student_family=sf)
            else:
                f = serializer.update(student, serializer.validated_data)
            request.session['student_family'] = f.id
            logging.debug(f'id = {f.id}, fam = {f.student_family}')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddStudentView(LoginRequiredMixin, View):
    def get(self, request, student_id=None):
        if student_id is not None:
            if request.user.is_board:
                g = get_object_or_404(Student, pk=student_id)
            else:
                sf = StudentFamily.objects.get(user=request.user)
                g = get_object_or_404(Student, id=student_id, student_family=sf)
            form = StudentForm(instance=g)
        else:
            form = StudentForm()
        return render(request, 'student_app/forms/student.html', {'form': form})

    def post(self, request, student_id=None):
        if student_id is not None:
            if request.user.is_board:
                g = get_object_or_404(Student, pk=student_id)
            else:
                sf = StudentFamily.objects.get(user=request.user)
                g = get_object_or_404(Student, id=student_id, student_family=sf)
            form = StudentForm(request.POST, instance=g)
        else:
            form = StudentForm(request.POST)
        if form.is_valid():
            logging.debug(form.cleaned_data)
            f = form.save(commit=False)
            f.student_family = StudentFamily.objects.filter(user=request.user)[0]
            request.session['student_family'] = f.id
            f.save()
            logging.debug(f'id = {f.id}, fam = {f.student_family}')
            return HttpResponseRedirect(reverse('registration:profile'))
        else:
            logging.debug(form.errors)

        return render(request, 'student_app/student_page.html', {'form': form})
# class AddStudentView(LoginRequiredMixin, BSModalCreateView):
#     template_name = 'student_app/student.html'
#     form_class = StudentForm
#     success_message = 'Success: Student was added'
#     success_url = reverse_lazy('registration:profile')
#
#     def post(self, request):
#         logging.debug(request.cleaned_data)
#         s = super().post(request)
#         logging.debug(s)
#
#         return s
        # student_family = StudentFamily.objects.filter(user=request.user)[0]
        # form = StudentForm(request.POST)
        # if form.is_valid():
        #     s = form.save(commit=False)
        #     s.student_family = student_family
        #     s.save()
        # else:
        #     logging.debug(form.errors)
        # return HttpResponseRedirect(reverse('registration:profile'))

