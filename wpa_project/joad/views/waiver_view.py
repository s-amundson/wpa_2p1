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
