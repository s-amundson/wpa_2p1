import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.http import JsonResponse
from ..models import BeginnerClass
from ..src import ClassRegistrationHelper
logger = logging.getLogger(__name__)


class ClassStatusView(LoginRequiredMixin, View):
    def get(self, request, class_id):
        bc = BeginnerClass.objects.get(pk=class_id)
        ec = ClassRegistrationHelper().enrolled_count(bc)
        logging.debug(ec)
        # logging.debug(bc.instructor_limit - ec['instructors'])
        return JsonResponse({'beginner': bc.beginner_limit - ec['beginner'],
                             'returnee': bc.returnee_limit - ec['returnee'],
                             'instructor': bc.instructor_limit - ec['staff'],
                             'status': bc.state, 'class_type': bc.class_type})

