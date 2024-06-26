from django.views.generic import TemplateView
import logging
logger = logging.getLogger(__name__)


class ThanksView(TemplateView):
    template_name = 'student_app/message.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['message'] = 'Thanks for contacting us.'
        logger.warning(self.kwargs)
        if self.kwargs.get('arg', '') == 'complaint':
            context['message'] += " Your comments and concerns have been submitted and will be reviewed by the board."
        return context
