from django.views.generic import ListView
from ..models import Article

import logging
logger = logging.getLogger(__name__)


class InfoView(ListView):
    model = Article
    template_name = 'info/info.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.kwargs.get('info', '').replace('_', ' ')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(page__page=self.kwargs.get('info', 'about'), status=1)
        return queryset.order_by('position')