from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from django.forms import model_to_dict
from django.utils import timezone

from ..forms import StaffReportForm
from event.models import Registration, VolunteerRecord
from src.mixin import BoardMixin
from student_app.models import Student, User

import logging
logger = logging.getLogger(__name__)


class StaffReportView(BoardMixin, FormView):
    template_name = 'program_app/staff_attend_report.html'
    form_class = StaffReportForm
    success_url = reverse_lazy('registration:index')
    start_date = None
    end_date = None

    def aware_date(self, date):
        if date is None:
            return None
        return timezone.datetime.combine(date, timezone.datetime.min.time(), timezone.get_current_timezone())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # staff_users = User.objects.filter(groups__name='staff', is_active=True)
        staff_students = Student.objects.filter(user__groups__name='staff', user__is_active=True).order_by('last_name')
        context['staff_list'] = []
        for i in staff_students:
            cr = Registration.objects.filter(student=i, pay_status__in=['paid', 'admin'])
            vr = VolunteerRecord.objects.filter(student=i, volunteer_points__gt=0)
            if self.start_date is not None:
                cr = cr.filter(event__event_date__gte=self.start_date)
                vr = vr.filter(event__event_date__gte=self.start_date)
            if self.end_date is not None:
                cr = cr.filter(event__event_date__lte=self.end_date)
                vr = vr.filter(event__event_date__lte=self.end_date)
            i_dict = model_to_dict(i)
            i_dict['registrations'] = len(cr)
            i_dict['attended'] = len(cr.filter(attended=True))
            i_dict['user'] = model_to_dict(i.user)
            i_dict['points'] = vr.aggregate(Sum('volunteer_points'))['volunteer_points__sum']
            context['staff_list'].append(i_dict)
        return context

    def form_valid(self, form):
        self.start_date = self.aware_date(form.cleaned_data.get('start_date', None))
        self.end_date = self.aware_date(form.cleaned_data.get('end_date', None))
        return self.form_invalid(form)


class StaffPointHistoryView(BoardMixin, ListView):
    model = VolunteerRecord
    template_name = 'program_app/staff_point_history.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(student=get_object_or_404(Student, pk=self.kwargs['student']))
        return queryset.order_by('-id')