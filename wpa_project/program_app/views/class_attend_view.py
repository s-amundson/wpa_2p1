from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.views.generic.base import View
from ..models import ClassRegistration
import logging
logger = logging.getLogger(__name__)


class ClassAttendView(UserPassesTestMixin, View):
    def post(self, request, registration):
        logging.debug(request.POST)
        cr = ClassRegistration.objects.get(pk=registration)
        if f'check_{cr.student.id}' in request.POST:
            cr.attended = request.POST[f'check_{cr.student.id}'] in ['true', 'on']

            logging.debug(f'safety_class date: {cr.student.safety_class} class_date: {cr.beginner_class.class_date}')
            if cr.attended:
                if cr.student.safety_class is None:
                    cr.student.safety_class = cr.beginner_class.class_date
                    cr.student.save()
            else:
                if cr.beginner_class.class_date.date() == cr.student.safety_class:
                    cr.student.safety_class = None
                    cr.student.save()
            cr.save()
            return JsonResponse({'error': False})
        return JsonResponse({'error': True})

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False
