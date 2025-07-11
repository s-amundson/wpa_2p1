from django.apps import apps
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..forms import CancelForm, CancelSetForm
from ..models import Registration
from ..tasks import cancel_pending
from src.mixin import StudentFamilyMixin
StudentFamily = apps.get_model(app_label='student_app', model_name='StudentFamily')

import logging
logger = logging.getLogger(__name__)


class CancelView(StudentFamilyMixin, FormView):
    template_name = 'event/cancel_form.html'
    form_class = CancelForm
    success_url = reverse_lazy('events:cancel')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formset = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_formset()
        return context

    def get_formset(self, **kwargs):
        if 'student_family' in self.kwargs:
            self.student_family = get_object_or_404(StudentFamily, pk=self.kwargs.get('student_family'))

        formset = modelformset_factory(Registration, form=CancelSetForm, can_delete=False, extra=0)
        data = None
        if self.request.method.lower() == 'post':
            data = self.request.POST
        formset = formset(
            queryset=Registration.objects.filter(
                event__event_date__gt=timezone.now(),
                student__in=self.student_family.student_set.all()).order_by('event__event_date'),
            data=data, **kwargs
            )
        return formset

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return form

    def form_valid(self, form):
        formset = self.get_formset()
        if formset.is_valid():
            cancel_list = []
            for f in formset:
                if f.cleaned_data['cancel']:
                    r = f.save(commit=False)
                    if r.pay_status in ['start', 'waiting']:
                        r.pay_status = 'canceled'
                    else:
                        r.pay_status = 'cancel_pending'
                    r.save()
                    cancel_list.append(r.id)
            cancel_pending.delay(cancel_list, form.cleaned_data['donate'])
        else:  # pragma: no cover
            logger.warning(formset.errors)
            logger.warning(formset.non_form_errors())
        if self.request.user.has_perm('student_app.board') and 'student_family' in self.kwargs:
            self.success_url = reverse_lazy('events:cancel',
                                            kwargs={'student_family': self.kwargs.get('student_family')})
        # return HttpResponseRedirect(reverse_lazy('events:cancel'))
        return super().form_valid(form)