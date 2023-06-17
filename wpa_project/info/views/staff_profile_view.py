from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q

from ..models import StaffProfile
from ..forms import StaffProfileForm
from student_app.models import Student

import logging
logger = logging.getLogger(__name__)


class StaffProfileFormView(UserPassesTestMixin, FormView):
    model = StaffProfile
    form_class = StaffProfileForm
    template_name = 'info/preview_form.html'
    success_url = reverse_lazy('info:staff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Staff Profile Form'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.kwargs.get('pk', None) is not None:
            kwargs['instance'] = get_object_or_404(StaffProfile, pk=self.kwargs['pk'])
        return kwargs

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_superuser
        return False


class StaffList(ListView):
    model = Student
    template_name = 'info/staff_list.html'

    def get_queryset(self):
        d = timezone.now() - timezone.timedelta(days=60)
        object_list = self.model.objects.filter(
            (Q(user__is_staff=True) &
            Q(registration__event__event_date__gte=d) &
            Q(registration__attended=True)) | Q(user__is_board=True)
        )

        return object_list.distinct().order_by('-user__is_board', '-user__is_instructor')
