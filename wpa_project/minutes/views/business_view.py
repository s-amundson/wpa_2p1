import logging

from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory

from ..forms import BusinessForm, BusinessFormset, BusinessUpdateForm
from ..models import Business, BusinessUpdate, Minutes

logger = logging.getLogger(__name__)


class BusinessView(UserPassesTestMixin, FormView):
    template_name = 'minutes/forms/business_form.html'
    form_class = BusinessForm
    success_url = reverse_lazy('registration:index')
    business = None
    business_id = None
    minutes = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_formset()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.business is not None:
            kwargs['instance'] = self.business
            kwargs['action_url'] = reverse_lazy('minutes:business',
                                                kwargs={'minutes': self.minutes.id, 'business_id': self.business.id})
        else:
            if self.minutes:
                kwargs['initial']['minutes'] = self.minutes
            kwargs['action_url'] = reverse_lazy('minutes:business', kwargs={'minutes': self.minutes.id})
        # kwargs['report'] = self.request.GET.get('report_index', None)
        return kwargs

    def get_formset(self, **kwargs):
        def calculate_extra():
            logger.warning(self.minutes)
            logger.warning(self.business)
            if self.minutes.end_time is not None:
                return 0
            if self.business is None:
                return 0
            if self.business.minutes == self.minutes:
                return 0
            if self.business.resolved is not None:
                return 0
            if not self.request.user.has_perm('student_app.board'):
                return 0
            if queryset.count() == 0:
                return 1
            if (queryset.last() is not None
                    and queryset.last().update_date + timezone.timedelta(hours=12) < timezone.now()):
                return 1
            return 0

        queryset = BusinessUpdate.objects.filter(business=self.business).order_by('update_date')

        formset = modelformset_factory(BusinessUpdate, form=BusinessUpdateForm, can_delete=False,
                                       formset=BusinessFormset, extra=calculate_extra())
        data = None
        if self.request.method.lower() == 'post':
            data = self.request.POST
        formset = formset(
            queryset=queryset,
            initial=[{'business': self.business}], data=data, minutes=self.minutes, **kwargs
            )
        return formset

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        formset = self.get_formset()
        if formset.is_valid():
            formset.save()

        else:  # pragma: no cover
            logger.warning(formset.errors)
            logger.warning(formset.non_form_errors())
        report = form.save()
        self.success_url = reverse_lazy('minutes:business', kwargs={'minutes': self.minutes.id, 'business_id': report.id})
        if form.cleaned_data.get('resolved_bool', False) and report.resolved is None:
            report.resolved = timezone.now()
        elif not form.cleaned_data.get('resolved_bool', False) and report.resolved:
            report.resolved = None

        report.save()
        self.business_id = report.id
        return super().form_valid(form)

    def test_func(self):
        logger.warning(self.kwargs)
        if self.request.user.is_authenticated:
            if 'business_id' in self.kwargs:
                self.business = get_object_or_404(Business, pk=self.kwargs.get('business_id'))
                self.business_id = self.kwargs.get('business_id', None)
            if 'minutes' in self.kwargs:
                self.minutes = get_object_or_404(Minutes, pk=self.kwargs.get('minutes'))
                logger.warning(self.minutes)
            else:
                return False
            if self.request.method == 'GET':
                return self.request.user.has_perm('student_app.members')
            return self.request.user.has_perm('student_app.board')
        return False
