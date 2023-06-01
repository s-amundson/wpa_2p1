from django.shortcuts import reverse
from django.utils import timezone
from facebook.views import PostList
from allauth.account.forms import LoginForm

from info.models import Announcement
import logging
logger = logging.getLogger(__name__)


class IndexView(PostList):
    template_name = 'student_app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        context['signup_url'] = reverse('account_signup')
        context['announcements'] = Announcement.objects.filter(
            status=1,
            end_date__gte=timezone.now(),
            begin_date__lte=timezone.now()
        )
        logger.warning(context['announcements'])
        return context
