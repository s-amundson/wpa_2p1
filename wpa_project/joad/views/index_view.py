from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.forms import model_to_dict

from student_app.models import Student
from ..models import Session
import logging
logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, View):
    """Landing page for JOAD"""
    def get(self, request):
        students = Student.objects.get(user=request.user).student_family.student_set.filter(is_joad=True)
        students = students.order_by('last_name', 'first_name')

        sessions = Session.objects.exclude(state='scheduled').exclude(state='canceled').exclude(state='recorded')
        sessions = sessions.order_by('start_date')
        session_list = []
        for session in sessions:
            s = model_to_dict(session)
            reg_list = []
            for student in students:
                reg = session.registration_set.filter(student=student, pay_status='paid')
                if len(reg) > 0:
                    logging.debug(reg)
                reg_list.append(len(reg) > 0)
            s['registrations'] = reg_list
            logging.debug(s)
            session_list.append(s)
        is_auth = len(students) > 0 or request.user.is_staff

        return render(request, 'joad/index.html',
                      {'session_list': session_list, 'students': students, 'is_auth': is_auth})
