from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404
import logging
from django.views.generic.base import View

from ..models import Student

logger = logging.getLogger(__name__)


class StudentTableView(LoginRequiredMixin, View):
    def get(self, request):
        student_family = get_object_or_404(Student, user=request.user).student_family
        students = []
        has_member = False
        if student_family is not None:
            sq = student_family.student_set.all()
            for s in sq:
                d = model_to_dict(s)
                if s.member_set.last() is not None:
                    has_member = True
                    # logging.debug(s.member_set.last().expire_date)
                    d['member_expire'] = s.member_set.last().expire_date
                students.append(d)

        return render(request, 'student_app/tables/student_table.html', {'students': students, 'has_member': has_member})
