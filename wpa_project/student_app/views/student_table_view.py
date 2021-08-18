from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
import logging
from django.views.generic.base import View

from ..models import StudentFamily

logger = logging.getLogger(__name__)


class StudentTableView(LoginRequiredMixin, View):
    def get(self, request):
        student_family = get_object_or_404(StudentFamily, user=request.user)
        students = student_family.student_set.all()
        return render(request, 'student_app/tables/student_table.html', {'students': students})
