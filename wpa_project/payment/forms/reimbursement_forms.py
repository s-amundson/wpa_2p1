from django import forms
from django.utils import timezone
from django.db.models import Sum

from ..models import Reimbursement, ReimbursementItem, ReimbursementVote

import logging
logger = logging.getLogger(__name__)


class ReimbursementForm(forms.ModelForm):
    class Meta:
        model = Reimbursement
        fields = ('student', 'title', 'status', 'note')

    def __init__(self, *args, **kwargs):
        if 'board_student' in kwargs:
            self.board_student = kwargs.pop('board_student')
        else:
            self.board_student = None
        super().__init__(*args, **kwargs)
        logging.debug(self.initial)
        self.fields['student'].widget = forms.HiddenInput()
        self.fields['note'].widget.attrs.update({'cols': 80, 'rows': 3})
        self.fields['note'].required = False
        if not (self.instance and self.instance.status == 'approved'):
            self.fields.pop('status')
        else:
            self.fields['status'].choices = [('approved', 'approved'), ('paid', 'paid')]
            # self.fields['title'].widget.attrs.update({'disabled': 'disabled'})
            self.fields['title'].disabled = True

    def save(self, commit=True):
        logger.warning(self.has_changed())
        if self.has_changed() and self.instance:
            if self.instance.status not in ['approved', 'paid']:
                self.instance.modified = timezone.now()
                self.instance.status = 'pending'
        return super().save(commit)


class ReimbursementItemForm(forms.ModelForm):
    class Meta:
        model = ReimbursementItem
        fields = ['id', 'reimbursement', 'amount', 'description', 'attachment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['attachment'].required = False
            logger.warning(self.instance)
            if self.instance.reimbursement.status not in ['pending', 'denied']:
                for f in ['amount', 'description', 'attachment']:
                    logger.warning(f)
                    self.fields[f].disabled = True


class ReimbursementVoteForm(forms.ModelForm):
    class Meta:
        model = ReimbursementVote
        fields = ('reimbursement', 'student', 'approve')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.warning(self.initial)
        self.fields['reimbursement'].widget = forms.HiddenInput()
        self.fields['student'].widget = forms.HiddenInput()
        self.fields['approve'].widget = forms.RadioSelect(choices=[(True, "Approve"), (False, "Deny")])

        self.sum = self.initial['reimbursement'].reimbursementitem_set.all().aggregate(Sum('amount'))['amount__sum']
        logger.warning(self.sum)
        self.title = 'Reimbursement'
        if self.initial['reimbursement'].status == 'pending':
            self.title = 'Reimbursement Vote'
        self.can_vote = self.initial['reimbursement'].status == 'pending'
        # self.fields['approve'].required = False
