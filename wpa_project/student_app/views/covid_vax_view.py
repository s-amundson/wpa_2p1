from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.views.generic.base import View
from ..models import Student
import logging
logger = logging.getLogger(__name__)


class CovidVaxView(UserPassesTestMixin, View):
    def post(self, request, student_id):
        # logging.debug(request.POST)
        student = Student.objects.get(pk=student_id)

        if f'covid_vax_{student.id}' in request.POST:
            student.covid_vax = request.POST[f'covid_vax_{student.id}'].lower() in ['true', 'on']
            student.save()
            return JsonResponse({'error': False})
        return JsonResponse({'error': True})

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False
