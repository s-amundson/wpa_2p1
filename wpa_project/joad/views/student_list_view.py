from student_app.views import StudentList
from ..forms import SearchColumnsForm

import logging
logger = logging.getLogger(__name__)


class StudentListView(StudentList):
    template_name = 'joad/student_list.html'
    form_class = SearchColumnsForm
    last_event = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_event'] = self.last_event
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_joad=True).order_by('last_name')
        if self.form.is_valid():
            self.last_event = self.form.cleaned_data['last_event']
        return queryset


