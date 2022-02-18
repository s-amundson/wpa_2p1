from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views.generic.base import View
from django.shortcuts import get_object_or_404

from student_app.forms import WaiverForm
from student_app.models import Student
from ..models import Attendance, JoadClass
from student_app.views import WaiverView as StudentWaiverView
import logging
logger = logging.getLogger(__name__)


class WaiverView(StudentWaiverView):
    def get_joad_class(self, class_id):
        logging.debug(class_id)
        if class_id is not None:
            jc = JoadClass.objects.get(pk=class_id)
            if jc is not None:
                return jc
            logging.debug(jc)
        return None

    def update_attendance(self):
        jc = self.get_joad_class(self.request.session.get('joad_class', None))
        a, created = Attendance.objects.get_or_create(joad_class=jc, student=self.student,
                                                      defaults={'attended': True})
        logging.debug(created)
        if not created:
            a.attended = True
            a.save()

# class WaiverView(UserPassesTestMixin, View):
#     def get(self, request, student_id):
#         student = get_object_or_404(Student, pk=student_id)
#         form = WaiverForm(student)
#         return render(request, 'program_app/class_sign_in.html',
#                       {'form': form, 'student': student, 'Img': student.signature,
#                        'is_signed': bool(student.signature)})
#
#     def get_joad_class(self, class_id):
#         logging.debug(class_id)
#         if class_id is not None:
#             jc = JoadClass.objects.get(pk=class_id)
#             if jc is not None:
#                 return jc
#             logging.debug(jc)
#         return None
#
#     def post(self, request, student_id):
#         student = get_object_or_404(Student, pk=student_id)
#         form = WaiverForm(student, request.POST)
#         if form.is_valid():
#             logging.debug('valid')
#             if form.make_pdf():
#                 jc = self.get_joad_class(request.session.get('joad_class', None))
#                 a, created = Attendance.objects.get_or_create(joad_class=jc, student=student,
#                                                               defaults={'attended': True})
#                 logging.debug(created)
#                 if not created:
#                     a.attended = True
#                     a.save()
#
#                 form.send_pdf()
#
#                 return HttpResponseRedirect(request.session.get('next_url', reverse('joad:index')))
#
#         logging.debug(form.errors)
#         return render(request, 'program_app/class_sign_in.html',
#                       {'form': form, 'student': student, 'Img': student.signature,
#                        'is_signed': bool(student.signature), 'message': 'invalid signature'})
#
#     def test_func(self):
#         if self.request.user.is_authenticated:
#             return self.request.user.is_staff
#         else:
#             return False