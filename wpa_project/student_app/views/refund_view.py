import uuid

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
import logging


from ..forms import ClassRegistrationForm
from ..models import BeginnerClass, ClassRegistration, Student, StudentFamily
from ..src.square_helper import line_item

logger = logging.getLogger(__name__)



class RefundView(LoginRequiredMixin, View):
    def get(self, request):
        students = StudentFamily.objects.filter(user=request.user)[0].student_set.all()
        form = ClassRegistrationForm(students)
        return render(request, 'student_app/class_registration.html', {'form': form})

    def post(self, request):
        logging.debug(request.POST)