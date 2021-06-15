import logging
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


class ClassAvailableView(LoginRequiredMixin, View):
    def get(self, request, class_id):
        bc = BeginnerClass.objects.get(pk=class_id)
        ec = ClassRegistrationHelper().enrolled_count(bc)
        return JsonResponse({'beginner': bc.beginner_limit - ec['beginner'],
                             'returnee': bc.returnee_limit - ec['returnee']})

