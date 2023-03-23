import logging
import uuid

from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from django.shortcuts import get_object_or_404
from ..forms import ElectionForm, ElectionCanidateForm, ElectionVoteForm
from ..models import Election, ElectionCandidate, ElectionPosition, ElectionVote, Member
from src.mixin import BoardMixin, MemberMixin, StudentFamilyMixin

logger = logging.getLogger(__name__)


class ElectionCandidateView(BoardMixin, FormView):
    template_name = 'student_app/form_as_p.html'
    form_class = ElectionCanidateForm
    success_url = reverse_lazy('registration:index')
    election = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'election_id' in self.kwargs:
            self.election = get_object_or_404(Election, pk=self.kwargs.pop('election_id'))
            kwargs['initial']['election'] =  self.election
        return kwargs

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        candidate = form.save()
        self.success_url = reverse_lazy('membership:election', kwargs={'election_id': self.election.id})
        return super().form_valid(form)

class ElectionListView(StudentFamilyMixin, ListView):
    model = Election
    template_name = 'membership/election_list.html'

class ElectionResultView(MemberMixin, ListView):
    template_name = 'membership/election_result.html'
    model = ElectionVote

    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        election = get_object_or_404(Election, pk=kwargs.get('election_id'))
        if election.state in ['scheduled', 'open']:
            logger.warning('This election is not closed')
            return HttpResponseRedirect(reverse_lazy('membership:election_list'))
        return dispatch

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        positions = ['president', 'vice_president', 'secretary', 'treasurer', 'member_at_large']
        for position in positions:
            result = self.object_list.values(position).annotate(Count('id')).order_by('-id__count')
            context[position] = []
            winning_count = 0
            for candidate in result:

                try:
                    context[position].append(
                        {'candidate':ElectionCandidate.objects.get(pk=candidate[position]),
                         'votes': candidate['id__count'],
                         'tie': candidate['id__count'] == winning_count})
                except ElectionCandidate.DoesNotExist:  # pragma: no cover
                    pass
                winning_count = candidate['id__count']
        logger.warning(context)
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(election__id=self.kwargs['election_id'])
        return queryset

class ElectionView(BoardMixin, FormView):
    template_name = 'membership/election_form.html'
    form_class = ElectionForm
    success_url = reverse_lazy('registration:index')
    election = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.election is not None:
            context['candidate_form'] = ElectionCanidateForm(initial={'election': self.election, 'state': 'scheduled'})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'election_id' in self.kwargs:
            logger.warning(self.kwargs)
            self.election = get_object_or_404(Election, pk=self.kwargs.pop('election_id'))
            kwargs['instance'] =  self.election
        return kwargs

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        election = form.save()
        self.success_url = reverse_lazy('membership:election', kwargs={'election_id': election.id})
        return super().form_valid(form)

class ElectionVoteView(MemberMixin, FormView):
    template_name = 'membership/election_vote_form.html'
    form_class = ElectionVoteForm
    success_url = reverse_lazy('payment:make_payment')
    election = None
    member = None

    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        self.election = get_object_or_404(Election, pk=kwargs.get('election_id'))
        if self.election.state == 'closed':
            logger.warning('This election is closed')
            return HttpResponseRedirect(reverse_lazy('membership:election_result',
                                                     kwargs={'election_id': self.election.id}))
        elif self.election.state == 'scheduled':
            return HttpResponseRedirect(reverse_lazy('membership:election_list'))
        return dispatch

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'election_id' in self.kwargs:
            logger.warning(self.kwargs)
            self.election = get_object_or_404(Election, pk=self.kwargs.pop('election_id'))
            kwargs['initial']['election'] =  self.election


        d = self.election.election_date
        d = d.replace(year=d.year-18)
        self.member = self.request.user.student_set.last().member_set.last()
        votes = ElectionVote.objects.filter(election=self.election, member=self.member)
        if len(votes):
            kwargs['instance'] = votes.last()
        kwargs['members'] = Member.objects.filter(pk=self.member.id)

        return kwargs

    def form_invalid(self, form):
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        if len(form.cleaned_data['member_at_large']) > 3:
            form.add_error('member_at_large', 'To many members selected.')
            return self.form_invalid(form)
        if not self.election.state == 'open':
            form.add_error('election', 'Cannot vote in this election at this time.')
            return self.form_invalid(form)
        vote = form.save()
        self.success_url = reverse_lazy('membership:election_vote', kwargs={'election_id': vote.election.id})
        return super().form_valid(form)