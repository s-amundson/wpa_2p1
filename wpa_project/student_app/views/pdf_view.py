from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django_sendfile import sendfile

# Create your views here.
from django.views import View
from ..models import Student


class PdfGetView(LoginRequiredMixin, View):
    def get(self, request, student_id, thumb=False):
        if request.user.has_perm('student_app.board'):
            student = get_object_or_404(Student, id=student_id)
        else:
            sf = get_object_or_404(Student, user=request.user).student_family
            student = get_object_or_404(Student, id=student_id, student_family=sf)

        if student.signature_pdf:
            return sendfile(request, student.signature_pdf.path)

        return HttpResponseForbidden()
