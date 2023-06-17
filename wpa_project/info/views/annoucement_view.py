from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from ..models import Announcement
from ..forms import AnnouncementForm

import logging
logger = logging.getLogger(__name__)


class AnnouncementFormView(UserPassesTestMixin, FormView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'info/preview_form.html'
    success_url = reverse_lazy('info:announcement_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Announcement Form'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.kwargs.get('pk', None) is not None:
            kwargs['instance'] = get_object_or_404(Announcement, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        form.save()
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_board
        return False


class AnnouncementList(ListView):
    """
    Return all announcements that are with status 1 (published) and order from the oldest one.
    """
    model = Announcement
    template_name = 'info/announcement_list.html'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['announcements'] = context.pop('object_list')
        return context

    def get_queryset(self):
        object_list = self.model.objects.filter(
            end_date__gte=timezone.now(),
            begin_date__lte=timezone.now(),
            status=1,
        )
        if self.request.user.is_authenticated and self.request.user.is_board:
            object_list = self.model.objects.filter(
                end_date__gte=timezone.now() - timezone.timedelta(days=30),
                begin_date__lte=timezone.now(),
            )
        return object_list.order_by('-created_at')
