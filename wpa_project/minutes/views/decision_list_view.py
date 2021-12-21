import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from ..models import Decision

logger = logging.getLogger(__name__)


class DecisionListView(LoginRequiredMixin, ListView):
    model = Decision
    template_name = 'minutes/decision_list.html'

    def get_queryset(self):
        return Decision.objects.all().order_by('-decision_date')