from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import View

from ..forms import StudentForm
from ..models import Student, StudentFamily

logger = logging.getLogger(__name__)


class AddStudentView(LoginRequiredMixin, View):
    def get(self, request, student_id=None):
        if student_id is not None:
            if request.user.is_board:
                g = get_object_or_404(Student, pk=student_id)
            else:
                sf = StudentFamily.objects.get(user=request.user)
                g = get_object_or_404(Student, id=student_id, student_family=sf)
            # g = Student.objects.get(id=student_id)
            form = StudentForm(instance=g)
        else:
            form = StudentForm()
        return render(request, 'student_app/student_page.html', {'form': form})

    def post(self, request):
        form = StudentForm(request.POST)
        if form.is_valid():
            logging.debug(form.cleaned_data)
            f = form.save(commit=False)
            f.student_family = StudentFamily.objects.filter(user=request.user)[0]
            request.session['student_family'] = f.id
            f.save()
            logging.debug(f'id = {f.id}, fam = {f.student_family}')
            return HttpResponseRedirect(reverse('registration:profile'))
        else:
            logging.debug(form.errors)

        return render(request, 'student_app/student_page.html', {'form': form})
# class AddStudentView(LoginRequiredMixin, BSModalCreateView):
#     template_name = 'student_app/student.html'
#     form_class = StudentForm
#     success_message = 'Success: Student was added'
#     success_url = reverse_lazy('registration:profile')
#
#     def post(self, request):
#         logging.debug(request.cleaned_data)
#         s = super().post(request)
#         logging.debug(s)
#
#         return s
        # student_family = StudentFamily.objects.filter(user=request.user)[0]
        # form = StudentForm(request.POST)
        # if form.is_valid():
        #     s = form.save(commit=False)
        #     s.student_family = student_family
        #     s.save()
        # else:
        #     logging.debug(form.errors)
        # return HttpResponseRedirect(reverse('registration:profile'))

