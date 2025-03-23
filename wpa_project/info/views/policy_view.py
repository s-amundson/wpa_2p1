from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.forms.models import model_to_dict
from ..models import Policy
from ..forms import PolicyTextForm

import logging
logger = logging.getLogger(__name__)


class PolicyFormView(FormView):
    model = Policy
    form_class = PolicyTextForm
    template_name = 'info/policy.html'
    success_url = reverse_lazy('info:announcement_list')
    policy = None
    version = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.policy:
            context['title'] = self.policy.title
            if self.version is None:
                context['current'] = self.policy.policytext_set.filter(status=1).first()
                context['history'] = self.policy.policytext_set.all()
        else:
            context['title'] = 'Policy Form'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'policy' in self.kwargs:
            self.policy = get_object_or_404(Policy, pk=self.kwargs.get('policy'))
            if self.kwargs.get('version', None) is not None:
                self.version = self.policy.policytext_set.get(pk=self.kwargs['version'])

        if self.policy is not None:
            if self.version is None:
                kwargs['initial'] = model_to_dict(self.policy.policytext_set.first())
                kwargs['initial']['status'] = 0
            else:
                # kwargs['initial'] = model_to_dict(self.version)
                kwargs['instance'] = self.version
            kwargs['initial']['title_text'] = self.policy.title
        return kwargs

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        if not self.request.user.is_board: # pragma: no cover
            return self.form_invalid(form)

        if self.policy is None:
            self.policy = Policy.objects.create(title=form.cleaned_data.get('title_text'))
        else:
            self.policy.title = form.cleaned_data.get('title_text')
            self.policy.save()
        pt = form.save(commit=False)
        pt.title = self.policy
        pt.save()

        self.success_url = reverse_lazy('info:policy', kwargs={'policy': self.policy.id})

        return super().form_valid(form)
