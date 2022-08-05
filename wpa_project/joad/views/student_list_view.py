from student_app.views import StudentList

import logging
logger = logging.getLogger(__name__)


class StudentListView(StudentList):
    template_name = 'joad/student_list.html'

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_joad=True)
        return queryset


