from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.utils import timezone

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

            if cr.attended:
                if cr.student.safety_class is None:
                    cr.student.safety_class = cr.event.event_date.date()
                    cr.student.save()
            else:
                if cr.event.event_date.date() == cr.student.safety_class:
                    cr.student.safety_class = None
                    cr.student.save()
            if cr.student.user is not None and cr.student.user.is_staff:
                points = 0
                if cr.event.volunteer_points and cr.attended:
                    if cr.reg_time <= cr.event.event_date - timezone.timedelta(days=3):
                        points = cr.event.volunteer_points
                    elif cr.reg_time <= cr.event.event_date - timezone.timedelta(days=1):
                        points = cr.event.volunteer_points / 2
                VolunteerRecord.objects.update_points(
                    cr.event,
                    cr.student,
                    points
                )
            cr.save()
            return JsonResponse({'attending': cr.attended, 'error': False,
                                 'name': f'{cr.student.first_name} {cr.student.last_name}'})
        return JsonResponse({'error': True})
