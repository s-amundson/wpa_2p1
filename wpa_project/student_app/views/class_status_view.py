import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import  HttpResponseForbidden
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from ..forms import CostsForm
from ..models import BeginnerClass
from ..src import ClassRegistrationHelper
logger = logging.getLogger(__name__)


class ClassStatusView(LoginRequiredMixin, View):
    def get(self, request, class_date):
        bc = BeginnerClass.objects.get(class_date=class_date)
        ec = ClassRegistrationHelper().enrolled_count(bc)
        return JsonResponse({'beginner': bc.beginner_limit - ec['beginner'],
                             'beginner_time': bc.class_date.strftime("%I %p"),
                             'returnee': bc.returnee_limit - ec['returnee'],
                             'returnee_time': (bc.class_date + timedelta(hours=2)).strftime("%I %p"),
                             'status': bc.state})

