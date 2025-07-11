from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import FormView

import logging
from django.http import JsonResponse

from ..forms import InstructorForm
logger = logging.getLogger(__name__)


class InstructorUpdateView(PermissionRequiredMixin, FormView):
    form_class = InstructorForm
    template_name = 'student_app/forms/instructor.html'
    permission_required = 'student_app.instructors'

    def form_invalid(self, form):
        logging.warning(form.errors)
        return JsonResponse({'status': "error"})

    def form_valid(self, form):
        self.request.user.instructor_expire_date = form.cleaned_data.get('instructor_expire_date',
                                                                         self.request.user.instructor_expire_date)
        self.request.user.instructor_level = form.cleaned_data.get('instructor_level',
                                                                   self.request.user.instructor_level)
        self.request.user.save()
        return JsonResponse({
            'status': 'SUCCESS',
            'expire_date': self.request.user.instructor_expire_date,
            'level': self.request.user.instructor_level
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs
