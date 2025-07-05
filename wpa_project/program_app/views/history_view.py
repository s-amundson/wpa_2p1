import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView
from event.models import Registration

logger = logging.getLogger(__name__)


class HistoryView(UserPassesTestMixin, TemplateView):
    model = Registration
    paginate_by = 100  # if pagination is desired
    student_family = None
    template_name = 'program_app/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = self.student_family.student_set.all()
        return context

    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.student_set.last():
            self.student_family = self.request.user.student_set.last().student_family
            if self.request.user.has_perm('student_app.board'):
                self.student_family = self.kwargs.get('family_id', self.student_family)
            return self.student_family is not None
        else:
            return False
