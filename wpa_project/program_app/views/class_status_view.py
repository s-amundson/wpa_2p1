import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.http import JsonResponse, HttpResponseBadRequest
from ..models import BeginnerClass
from ..src import ClassRegistrationHelper
logger = logging.getLogger(__name__)


class ClassStatusView(LoginRequiredMixin, View):
    def get(self, request, class_id):
        if class_id == 'null':
            return HttpResponseBadRequest()
        try:
            bc = BeginnerClass.objects.get(pk=class_id)
            ec = ClassRegistrationHelper().enrolled_count(bc)
            return JsonResponse({'beginner': bc.beginner_limit - ec['beginner'],
                                 'returnee': bc.returnee_limit - ec['returnee'],
                                 'instructor': bc.instructor_limit - ec['staff'],
                                 'status': bc.event.state, 'class_type': bc.class_type})
        except ValueError:  # pragma: no cover
            return HttpResponseBadRequest()

