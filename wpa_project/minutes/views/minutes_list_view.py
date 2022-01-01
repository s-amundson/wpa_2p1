import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from ..models import Minutes

logger = logging.getLogger(__name__)


class MinutesListView(LoginRequiredMixin, ListView):
    model = Minutes
    template_name = 'minutes/minutes_list.html'

    def get_queryset(self):
        return Minutes.objects.all().order_by('-meeting_date')