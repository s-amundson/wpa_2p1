from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.views.generic import FormView
from django.urls import reverse_lazy

from ..models import BeginnerClass, ClassRegistration
from ..forms import ClassAttendanceForm
from ..src import ClassRegistrationHelper
import logging
logger = logging.getLogger(__name__)


class ClassAttendListView(UserPassesTestMixin, FormView):
    template_name = 'program_app/class_attendance.html'
    form_class = ClassAttendanceForm
    success_url = reverse_lazy('registration:index')
    beginner_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['beginner_class'] = self.beginner_class.id
        return context

    def get_form(self):
        return self.form_class(self.beginner_class, **self.get_form_kwargs())

    def test_func(self):
        if self.request.user.is_authenticated:
            bid = self.kwargs.get('beginner_class', None)
            if bid is None:
                return False
            self.beginner_class = get_object_or_404(BeginnerClass, pk=bid)
            return self.request.user.is_staff
        else:
            return False


class ClassAttendView(UserPassesTestMixin, View):
    def post(self, request, registration):
        # logging.debug(request.POST)
        cr = ClassRegistration.objects.get(pk=registration)
        if f'check_{cr.student.id}' in request.POST:
            cr.attended = request.POST[f'check_{cr.student.id}'] in ['true', 'on']

            logging.debug(f'safety_class date: {cr.student.safety_class} class_date: {cr.beginner_class.event.event_date}')
            if cr.attended:
                if cr.student.safety_class is None:
                    cr.student.safety_class = cr.beginner_class.event.event_date.date()
                    cr.student.save()
            else:
                if cr.beginner_class.event.event_date.date() == cr.student.safety_class:
                    cr.student.safety_class = None
                    cr.student.save()
            cr.save()
            return JsonResponse({'attending': cr.attended, 'error': False,
                                 'name': f'{cr.student.first_name} {cr.student.last_name}'})
        return JsonResponse({'error': True})

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False
