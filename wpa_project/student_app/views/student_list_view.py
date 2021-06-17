import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_list_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic import ListView
from django.utils import timezone
# from django.db.models import model
# from django.core.exceptions import ObjectDoesNotExist

from ..forms import BeginnerClassForm, ClassAttendanceForm
from ..models import Student, BeginnerClass, ClassRegistration, CostsModel
from ..src import SquareHelper

logger = logging.getLogger(__name__)


class StudentList(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'student_app/student_list.html')

