from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
import logging

from ..forms import ThemeForm
from program_app.src import ClassRegistrationHelper
logger = logging.getLogger(__name__)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'student_app/profile.html'
    """Shows the users profile"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['this_student'] = self.request.user.student_set.last()
        context['theme_form'] = ThemeForm(initial={'theme': 'dark' if self.request.user.dark_theme else 'light'})
        context['student_family'] = None
        if context['this_student'] is not None:
            context['student_family'] = context['this_student'].student_family
        if context['student_family'] is not None:
            context['students'] = context['student_family'].student_set.all()
        context['attend_history'] = ClassRegistrationHelper().attendance_history_queryset(context['student_family'])
        return context


