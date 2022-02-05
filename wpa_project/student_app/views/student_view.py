from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
import logging
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.base import View
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
        # logging.debug(request.data)
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


class AddStudentView(LoginRequiredMixin, View):
    def get(self, request, student_id=None):
        student = {'is_user': False, 'this_user': False, 'id': student_id, 'is_joad': False, 'joad_age': False}
        if student_id is not None:
            if request.user.is_board:
                g = get_object_or_404(Student, pk=student_id)
                student['is_joad'] = g.is_joad
                # student_is_user = g.user_id
            else:
                sf = Student.objects.get(user=request.user).student_family
                g = get_object_or_404(Student, id=student_id, student_family=sf)
                student['is_user'] = g.user_id
                student['is_joad'] = g.is_joad
                student['this_user'] = (g.user == request.user)
            age = StudentHelper().calculate_age(g.dob)
            student['joad_age'] = 8 < age < 21
            form = StudentForm(instance=g, student_is_user=student['is_user'])
        else:
            s = Student.objects.filter(user=request.user)
            # logging.debug(s.count())
            if s.count() == 0:
                form = StudentForm(initial={'email': request.user.email}, student_is_user=True)
                student['is_user'] = 0
                student['this_user'] = True
            else:
                form = StudentForm()
        # logging.debug(student['is_user'])
        d = {'form': form, 'student': student}
        return render(request, 'student_app/forms/student.html', d)

    def post(self, request, student_id=None):
        if student_id is not None:
            if request.user.is_board:
                g = get_object_or_404(Student, pk=student_id)
            else:
                sf = Student.objects.get(user=request.user).student_family
                g = get_object_or_404(Student, id=student_id, student_family=sf)
            form = StudentForm(request.POST, instance=g)
        else:
            form = StudentForm(request.POST)
        # logging.debug(request.POST)
        if form.is_valid():
            logging.debug(form.cleaned_data)
            if request.user.is_board:
                f = form.save()
            else:
                f = form.save(commit=False)
                sf = Student.objects.get(user=request.user).student_family
                logging.debug(sf.id)
                f.student_family = sf
                request.session['student_family'] = sf.id
                f.save()

            # logging.debug(f'id = {f.id}, fam = {f.student_family__id}')
            return HttpResponseRedirect(reverse('registration:profile'))
        else:
            logging.debug(form.errors)

        return render(request, 'student_app/student_page.html', {'form': form})


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
