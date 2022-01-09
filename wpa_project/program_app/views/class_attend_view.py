from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.views.generic.base import View
from ..models import ClassRegistration
import logging
logger = logging.getLogger(__name__)


class ClassAttendView(UserPassesTestMixin, View):
    def post(self, request, registration):
        cr = ClassRegistration.objects.get(pk=registration)
        if f'check_{cr.student.id}' in request.POST:
            cr.attended = request.POST[f'check_{cr.student.id}'] in ['true', 'on']
            cr.save()
            return JsonResponse({'error': False})
        if f'covid_vax_{cr.student.id}' in request.POST:
            cr.student.covid_vax = request.POST[f'covid_vax_{cr.student.id}'] in ['true', 'on']
            cr.student.save()
            return JsonResponse({'error': False})
        return JsonResponse({'error': True})

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False
