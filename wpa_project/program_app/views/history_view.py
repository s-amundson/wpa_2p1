import logging
import csv
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponse
from ..src import ClassRegistrationHelper
from ..models import ClassRegistration
from student_app.models import Student
logger = logging.getLogger(__name__)


class HistoryView(UserPassesTestMixin, TemplateView):
    model = ClassRegistration
    paginate_by = 100  # if pagination is desired
    student_family = None
    template_name = 'program_app/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attend_history'] = ClassRegistrationHelper().attendance_history_queryset(self.student_family)
        return context

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.student_set.last():
            self.student_family = self.request.user.student_set.last().student_family
            if self.request.user.is_board:
                self.student_family = self.kwargs.get('family_id', self.student_family)
            return self.student_family is not None
        else:
            return False
