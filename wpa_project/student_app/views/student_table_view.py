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


class StudentTableView(LoginRequiredMixin, View):
    def get(self, request):
        student_family = get_object_or_404(StudentFamily, user=request.user)
        students = student_family.student_set.all()
        return render(request, 'student_app/tables/student_table.html', {'students': students})
