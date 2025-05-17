import logging
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.shortcuts import get_object_or_404

from ..forms import PollForm, PollVoteForm
from ..models import Poll, PollType, PollVote
from src.mixin import BoardMixin, StudentFamilyMixin

logger = logging.getLogger(__name__)


class PollListView(StudentFamilyMixin, ListView):
    model = Poll
    template_name = 'minutes/poll_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll_type'] = self.request.GET.get('poll_type', 'poll')
        return context

    def get_queryset(self):
        queryset =  super().get_queryset().filter(poll_type__poll_type= self.request.GET.get('poll_type', 'poll'))
        return queryset.order_by('-poll_date')


class PollView(BoardMixin, FormView):
    template_name = 'minutes/poll.html'
    form_class = PollForm
    success_url = reverse_lazy('minutes:poll_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # logger.debug(self.request.GET)
        context['poll_type'] = self.request.GET.get('poll_type', 'poll')
        return context

    def get_form_kwargs(self):
        # logger.warning(self.kwargs)
        kwargs = super().get_form_kwargs()
        if 'pk' in self.kwargs:
            kwargs['instance'] = get_object_or_404(Poll, pk=self.kwargs.get('pk'))
        else:
            pt = get_object_or_404(PollType, poll_type=self.request.GET.get('poll_type', 'poll'))

            kwargs['initial']['poll_type'] = kwargs['initial'].get('poll_type', pt)
            kwargs['initial']['minutes'] = kwargs['initial'].get('minutes', self.request.GET.get('minutes', None))
            kwargs['initial']['business'] = kwargs['initial'].get('business', self.request.GET.get('business', None))
        return kwargs

    def form_invalid(self, form): # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        poll = form.save()
        self.success_url += f"?poll_type={poll.poll_type}"
        return super().form_valid(form)


class PollVoteView(BoardMixin, FormView):
    template_name = 'minutes/poll.html'
    form_class = PollVoteForm
    success_url = reverse_lazy('minutes:poll_list')
    poll = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.debug(self.request.GET)
        context['poll_type'] = self.poll.poll_type
        return context

    def get_form_kwargs(self):
        logger.warning(self.kwargs)
        kwargs = super().get_form_kwargs()
        kwargs['initial']['poll'] = self.poll = get_object_or_404(Poll, pk=self.kwargs.get('poll', None))
        kwargs['initial']['user'] = self.request.user
        vote = self.poll.pollvote_set.filter(user=self.request.user)
        if vote.count():
            kwargs['instance'] = vote.last()
        return kwargs

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # logger.warning(form.cleaned_data)
        # logger.warning(self.request.POST)
        vote = form.save()
        self.success_url += f"?poll_type={vote.poll.poll_type}"
        return super().form_valid(form)
