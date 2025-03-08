import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from ..forms import MinutesSearchForm
from ..models import Minutes

logger = logging.getLogger(__name__)


class MinutesListView(LoginRequiredMixin, ListView):
    model = Minutes
    template_name = 'minutes/minutes_list.html'
    paginate_by = 20
    form_class = MinutesSearchForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['form'] = self.form_class(initial=self.request.GET)
        return context

    def get_queryset(self):
        logger.debug(self.request.GET)
        self.form = self.form_class(self.request.GET)
        object_list = self.model.objects.all()
        if self.form.is_valid():
            if self.form.cleaned_data['begin_date']:
                object_list = object_list.filter(meeting_date__date__gte=self.form.cleaned_data['begin_date'])
            if self.form.cleaned_data['end_date']:
                object_list = object_list.filter(meeting_date__date__lte=self.form.cleaned_data['end_date'])
            if self.form.cleaned_data['search_string']:
                logger.debug(self.form.cleaned_data['search_string'])
                matching_objects = object_list.filter(discussion__icontains=self.form.cleaned_data['search_string'])
                if self.form.cleaned_data['reports']:
                    matching_objects = matching_objects | object_list.filter(
                        report__report__icontains=self.form.cleaned_data['search_string'])
                if self.form.cleaned_data['business']:
                    matching_objects = matching_objects | object_list.filter(
                        business__business__icontains=self.form.cleaned_data['search_string'])
                    matching_objects = matching_objects | object_list.filter(
                        business__businessupdate__update_text__icontains=self.form.cleaned_data['search_string'])
                object_list = matching_objects

        return object_list.order_by('-meeting_date')
