from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from ..models import BeginnerClass

import logging
logger = logging.getLogger(__name__)


class WaitListView(UserPassesTestMixin, ListView):
    beginner_class = None
    template_name = 'program_app/wait_list.html'
    success_url = reverse_lazy('registration:index')

    def get_queryset(self):
        registrations = self.beginner_class.event.registration_set.filter(pay_status__in=['admin', 'waiting', 'paid'])
        queryset = registrations.filter(student__in=self.request.user.student_set.last().student_family.student_set.all())
        object_list = []
        for cr in queryset.order_by('modified'):
            if self.beginner_class.class_type == 'beginner':
                num_reg_students = self.beginner_class.beginner_limit
            elif self.beginner_class.class_type == 'returnee':
                num_reg_students = self.beginner_class.returnee_limit
            else:
                num_reg_students = self.beginner_class.beginner_limit + self.beginner_class.returnee_limit
            object_list.append({
                'id': cr.id,
                'first_name': cr.student.first_name,
                'last_name': cr.student.last_name,
                'pay_status': cr.pay_status,
                'index': len(registrations.filter(reg_time__lte=cr.reg_time)) - num_reg_students,
                'reg_time': cr.reg_time
            })
        return object_list

    def test_func(self):
        if self.request.user.is_authenticated:
            bid = self.kwargs.get('beginner_class', None)
            if bid is None:
                return False
            self.beginner_class = get_object_or_404(BeginnerClass, pk=bid)
            return True
