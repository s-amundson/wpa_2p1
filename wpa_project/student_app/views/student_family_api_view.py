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
from ..serializers import StudentFamilySerializer

logger = logging.getLogger(__name__)


class StudentFamilyApiView(LoginRequiredMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_students(self, request, family_id):
        logging.debug(family_id)
        if family_id is None:
            student_family = StudentFamily.objects.filter(user=request.user)
            if student_family.exists():
                self.serializer = StudentFamilySerializer(instance=student_family[0])
            else:
                self.serializer = StudentFamilySerializer()
        else:
            student_family = get_object_or_404(StudentFamily, pk=family_id)
            self.serializer = StudentFamilySerializer(instance=student_family)

    def get(self, request, family_id=None):

        self.get_students(request, family_id)
        message = request.session.get('message', '')
        logging.debug(message)
        return render(request, 'student_app/forms/student_family_form.html', {'form': self.serializer, 'message': message})

    def post(self, request, family_id=None):
        logging.debug(family_id)
        if family_id is None:
            serializer = StudentFamilySerializer(request.data)
        else:
            student_family = get_object_or_404(StudentFamily, pk=family_id)
            logging.debug(student_family)
            serializer = StudentFamilySerializer(student_family, data=request.data)

        if serializer.is_valid():
            logging.debug('valid')
            if family_id is None:
                f = serializer.save()
            else:
                f = serializer.update(student_family, serializer.validated_data)

            f.user.add(request.user)
            # request.session['student_family'] = f.id
            logging.debug(f'id = {f.id}, user = {f.user}')
            return Response(serializer.data)

        else:
            logging.debug(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
