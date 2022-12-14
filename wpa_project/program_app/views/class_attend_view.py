from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.views.generic import FormView
from django.urls import reverse_lazy

from ..forms import ClassAttendanceForm
from event.models import Event, Registration, VolunteerRecord
from src.mixin import StaffMixin
import logging
logger = logging.getLogger(__name__)


class ClassAttendListView(StaffMixin, FormView):
    template_name = 'program_app/class_attendance.html'
    form_class = ClassAttendanceForm
    success_url = reverse_lazy('registration:index')
    beginner_class = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        eid = self.kwargs.get('event', None)
        kwargs['event'] = get_object_or_404(Event, pk=eid)
        return kwargs


class ClassAttendView(StaffMixin, View):
    def post(self, request, registration):
        cr = Registration.objects.get(pk=registration)
        if f'check_{cr.student.id}' in request.POST:
            cr.attended = request.POST[f'check_{cr.student.id}'] in ['true', 'on']

            logging.debug(f'safety_class date: {cr.student.safety_class} class_date: {cr.event.event_date}')
            if cr.attended:
                if cr.student.safety_class is None:
                    cr.student.safety_class = cr.event.event_date.date()
                    cr.student.save()
                elif cr.student.user is not None and cr.student.user.is_staff:
                    VolunteerRecord.objects.update_points(
                        cr.event,
                        cr.student,
                        cr.event.volunteer_points
                    )

            else:
                if cr.event.event_date.date() == cr.student.safety_class:
                    cr.student.safety_class = None
                    cr.student.save()
            cr.save()
            return JsonResponse({'attending': cr.attended, 'error': False,
                                 'name': f'{cr.student.first_name} {cr.student.last_name}'})
        return JsonResponse({'error': True})
