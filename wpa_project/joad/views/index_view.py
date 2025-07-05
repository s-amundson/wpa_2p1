from django.utils import timezone
from django.forms import model_to_dict

from ..models import Session
from .joad_event_view import JoadEventListView
import logging
logger = logging.getLogger(__name__)


class IndexView(JoadEventListView):
    """Landing page for JOAD"""
    model = Session
    template_name = 'joad/index.html'

    def __init__(self):
        super().__init__()
        self.session_list = []
        self.past_events = False
        self.has_joad = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_list'] = self.session_list
        context['has_joad'] = self.has_joad
        if self.request.user.has_perm('student_app.staff') or self.students:
            context['is_auth'] = len(self.students) > 0 or self.request.user.has_perm('student_app.staff')
        else:
            context['is_auth'] = False
        context['students'] = self.students
        return context

    def get_queryset(self):
        session_date = timezone.now() - timezone.timedelta(days=8*7)
        sessions = Session.objects.filter(start_date__gte=session_date)
        if not self.request.user.has_perm('student_app.staff'):
            sessions = sessions.filter(state__in=['scheduled', 'open', 'full', 'closed'])
        sessions = sessions.order_by('start_date')
        self.has_joad = self.request.user.has_perm('student_app.staff')
        for session in sessions:
            s = model_to_dict(session)
            reg_list = []
            if self.students:
                for student in self.students:
                    reg_id = None
                    reg_status = 'not registered'
                    # logger.debug(student)
                    if student.is_joad:
                        self.has_joad = True
                        reg = session.registration_set.filter(student=student)#  .order_by('id')
                        # logger.debug(reg)
                        if len(reg.filter(pay_status='paid')) > 0:
                            reg_status = 'registered'
                            # logger.debug(reg)
                        elif len(reg.filter(pay_status='start')) > 0:
                            reg_status = 'start'
                            reg_id = reg.filter(pay_status='start').last().id
                    reg_list.append({'is_joad': student.is_joad, 'reg_status': reg_status, 'reg_id': reg_id})
            s['registrations'] = reg_list
            # logger.debug(s)
            self.session_list.append(s)
