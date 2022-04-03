from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.views.generic import FormView
from django.utils import timezone
from django.urls import reverse_lazy
from django.forms import model_to_dict

from ..forms import StaffReportForm
from ..models import BeginnerClass, ClassRegistration
from student_app.models import Student, User

import logging
logger = logging.getLogger(__name__)


class StaffReportView(UserPassesTestMixin, FormView):
    template_name = 'program_app/staff_attend_report.html'
    form_class = StaffReportForm
    success_url = reverse_lazy('registration:index')
    start_date = None
    end_date = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        staff_students = Student.objects.filter(user__in=staff_users).order_by('last_name')
        context['staff_list'] = []
        for i in staff_students:
            cr = ClassRegistration.objects.filter(student=i, pay_status__in=['paid', 'admin'])
            bc = BeginnerClass.objects.all()
            if self.start_date is not None:
                bc = bc.filter(class_date__gte=self.start_date)
            if self.end_date is not None:
                bc = bc.filter(class_date__lte=self.end_date)
            cr = cr.filter(beginner_class__in=bc)
            i_dict = model_to_dict(i)
            logging.debug(i_dict)
            i_dict['registrations'] = len(cr)
            i_dict['attended'] = len(cr.filter(attended=True))
            i_dict['user'] = model_to_dict(i.user)
            context['staff_list'].append(i_dict)
        return context

    def form_valid(self, form):
        self.start_date = form.cleaned_data.get('start_date', None)
        self.end_date = form.cleaned_data.get('end_date', None)
        return self.form_invalid(form)

    def test_func(self):
        return self.request.user.is_board
