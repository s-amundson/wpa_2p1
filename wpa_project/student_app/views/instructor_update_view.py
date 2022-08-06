from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
import logging
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.views.generic.base import View

from ..forms import InstructorForm
logger = logging.getLogger(__name__)


class InstructorUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_instructor:
            raise Http404("Not an instructor.")
        form = InstructorForm(instance=request.user)
        return render(request, 'student_app/forms/instructor.html', {'form': form})

    def post(self, request):
        if not request.user.is_instructor:
            raise Http404("Not an instructor.")
        form = InstructorForm(request.POST)
        if form.is_valid():
            request.user.instructor_expire_date = form.cleaned_data.get('instructor_expire_date', request.user.instructor_expire_date)
            request.user.instructor_level = form.cleaned_data.get('instructor_level', request.user.instructor_level)
            request.user.save()
            return JsonResponse({
                'status': 'SUCCESS',
                'expire_date': request.user.instructor_expire_date,
                'level': request.user.instructor_level
            })
        else:
            logging.warning(form.errors)
            return JsonResponse({'status': "error"})
