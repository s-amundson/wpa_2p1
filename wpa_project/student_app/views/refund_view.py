from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin

import logging
from ..forms import ClassRegistrationForm
from ..models import StudentFamily
logger = logging.getLogger(__name__)


class RefundView(LoginRequiredMixin, View):
    def get(self, request):
        students = StudentFamily.objects.filter(user=request.user)[0].student_set.all()
        form = ClassRegistrationForm(students)
        return render(request, 'student_app/class_registration.html', {'form': form})

    def post(self, request):
        logging.debug(request.POST)
