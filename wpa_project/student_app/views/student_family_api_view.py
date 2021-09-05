from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
import logging
from django.http import HttpResponseBadRequest

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

from ..models import Student, StudentFamily
from ..serializers import StudentFamilySerializer

logger = logging.getLogger(__name__)


class StudentFamilyApiView(LoginRequiredMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, family_id=None):
        if family_id is None:
            try:
                student_family = Student.objects.get(user=request.user).student_family
                serializer = StudentFamilySerializer(instance=student_family)
            except Student.DoesNotExist:
                serializer = StudentFamilySerializer()
        else:
            student_family = get_object_or_404(Student, user=request.user).student_family
            if student_family.id == family_id:
                serializer = StudentFamilySerializer(instance=student_family)
            elif request.user.is_staff:
                student_family = get_object_or_404(StudentFamily, pk=family_id)
                serializer = StudentFamilySerializer(instance=student_family)
            else:
                return HttpResponseBadRequest()
        return Response(serializer.data)

    def post(self, request, family_id=None):
        logging.debug(family_id)
        if family_id is None:
            # check if user is part of family so that we don't make duplicate enteries
            try:
                student_family = Student.objects.get(user=request.user).student_family
            except Student.DoesNotExist:
                student_family = None
            if student_family is not None:
                family_id = student_family.id
                serializer = StudentFamilySerializer(instance=student_family, data=request.data)
            else:
                serializer = StudentFamilySerializer(data=request.data)
        else:
            student_family = get_object_or_404(Student, user=request.user).student_family
            if student_family.id == family_id:
                serializer = StudentFamilySerializer(student_family, data=request.data)
            elif request.user.is_staff:
                student_family = get_object_or_404(StudentFamily, pk=family_id)
                serializer = StudentFamilySerializer(student_family, data=request.data)
            else:
                return HttpResponseBadRequest()

        if serializer.is_valid():
            logging.debug('valid')
            if family_id is None:
                f = serializer.save()
                s = Student.objects.get(user=request.user)
                s.student_family = f
                s.save()
            else:
                f = serializer.update(student_family, serializer.validated_data)
                f.save()
            logging.debug(serializer.data)
            return Response(serializer.data)

        else:
            logging.debug(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
