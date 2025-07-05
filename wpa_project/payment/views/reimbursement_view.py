from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.forms import modelformset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..forms import ReimbursementForm, ReimbursementItemForm, ReimbursementVoteForm
from ..models import Reimbursement, ReimbursementItem, ReimbursementVote
from src.mixin import StudentFamilyMixin, BoardMixin

import logging
logger = logging.getLogger(__name__)


class ReimbursementFormView(StudentFamilyMixin, FormView):
    template_name = 'payment/reimbursement_form.html'
    form_class = ReimbursementForm
    success_url = reverse_lazy('payment:reimbursement_list')
    instance = None

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.warning(form.cleaned_data)
        formset = self.get_formset()
        if formset.is_valid():
            logger.warning(formset.cleaned_data)
            self.instance = form.save()
            logger.warning(self.instance.id)
            formset = self.get_formset()
            formset.save()
            if self.request.user.has_perm('student_app.board') and self.instance.student == self.request.user.student_set.last() \
                    and self.instance.status in ['pending', 'denied']:
                v, created = ReimbursementVote.objects.get_or_create(
                    reimbursement=self.instance,
                    student=self.instance.student,
                    defaults={'approve': True}
                )
                if not created:
                    v.timestamp = timezone.now()
                    v.save()
            return super().form_valid(form)
        else:  # pragma: no cover
            logger.warning(formset.errors)
            logger.warning(formset.non_form_errors())
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['formset'] = self.get_formset()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'pk' in self.kwargs:
            self.instance = get_object_or_404(Reimbursement, pk=self.kwargs.get('pk'))
            kwargs['board_student'] = self.instance.student == self.request.user.student_set.last() and self.request.user.has_perm('student_app.board')
        else:
            kwargs['initial']['student'] = self.request.user.student_set.last()
            kwargs['board_student'] = self.request.user.has_perm('student_app.board')
        logger.warning(kwargs['board_student'])
        kwargs['instance'] = self.instance
        return kwargs

    def get_formset(self, **kwargs):
        data = None
        files = None
        extra = 4
        if self.request.method.lower() == 'post':
            data = self.request.POST
            files = self.request.FILES
        if self.instance and self.instance.status in ['approved', 'paid']:
            extra = 0
        formset = inlineformset_factory(
            Reimbursement,
            ReimbursementItem,
            form=ReimbursementItemForm,
            can_delete=False,
            extra=extra)

        return formset(
            data=data, files=files, instance=self.instance, **kwargs
            )


class ReimbursementListView(StudentFamilyMixin, ListView):
    model = Reimbursement
    template_name = 'payment/reimbursement_list.html'
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['edit_status'] = ['pending', 'denied']
        return context

    def get_queryset(self):
        return Reimbursement.objects.all().order_by('-created')


class ReimbursementVoteView(BoardMixin, FormView):
    template_name = 'payment/reimbursement_vote.html'
    form_class = ReimbursementVoteForm
    success_url = reverse_lazy('payment:reimbursement_list')
    reimbursement = None
    student = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial']['reimbursement'] = self.reimbursement
        kwargs['initial']['student'] = self.student
        votes = ReimbursementVote.objects.filter(reimbursement=self.reimbursement, student=self.student)
        if votes:
            kwargs['instance'] = votes.last()
            logger.warning(votes.last())
        return kwargs

    def form_invalid(self, form):  # pragma: no cover
        logger.warning(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        vote = form.save()
        votes = ReimbursementVote.objects.get_vote_count(self.reimbursement)
        if votes['yes'] > 3:
            self.reimbursement.status = 'approved'
            self.reimbursement.save()
        if votes['no'] > 3:
            self.reimbursement.status = 'denied'
            self.reimbursement.save()
        logger.warning(votes)

        return super().form_valid(form)

    def test_func(self):
        if super().test_func():
            self.reimbursement = get_object_or_404(Reimbursement, pk=self.kwargs.get('pk'))
            self.student = self.request.user.student_set.last()
            return True
        return False  # pragma: no cover
