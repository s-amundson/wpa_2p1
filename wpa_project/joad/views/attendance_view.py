from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404
import logging
from django.views.generic.base import View
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.views.generic.list import ListView

from ..models import Attendance, Registration, JoadClass
from student_app.models import Student
from ..forms import ClassForm

logger = logging.getLogger(__name__)


class AttendView(UserPassesTestMixin, View):
    def post(self, request, class_id=None):
        logging.debug(request.POST.dict())
        jc = get_object_or_404(JoadClass, pk=class_id)
        student = None
        attend = False
        for k,v in request.POST.items():
            logging.debug(k)
            logging.debug(k.split('_'))
            key = k.split('_')
            if key[0] == 'check':
                student = get_object_or_404(Student, pk=int(key[1]))
                attend = v in ['true', 'on']
        if student:
            a, created = Attendance.objects.get_or_create(joad_class=jc, student=student, defaults={'attended': attend})
            if not created:
                a.attended = attend
                a.save()
            return JsonResponse({'attend': attend, 'error': False})

        return JsonResponse({'attend': attend, 'error': True})

    def test_func(self):
        return self.request.user.is_staff


class AttendanceListView(UserPassesTestMixin, ListView):
    model = Registration
    template_name = 'joad/attendance.html'
    joad_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['joad_class'] = self.joad_class.id
        logging.debug(context)
        return context

    def get_queryset(self):
        cid = self.kwargs.get("class_id", None)
        self.joad_class = get_object_or_404(JoadClass, pk=cid)
        registrations = self.model.objects.filter(session=self.joad_class.session, pay_status='paid').order_by(
            'student__last_name')
        logging.debug(registrations)
        attendance = self.joad_class.attendance_set.all()
        logging.debug(attendance)
        object_list = []
        for registration in registrations:
            checked = False
            a = attendance.filter(student=registration.student)
            if len(a) > 0:
                checked = a[0].attended
            object_list.append({'first_name': registration.student.first_name,
                                'last_name': registration.student.last_name,
                                'check_id': f'check_{registration.student.id}',
                                'id': registration.student.id,
                                'checked': checked,
                                'signature': bool(registration.student.signature)
                                })

        return object_list

    def test_func(self):
        return self.request.user.is_staff
