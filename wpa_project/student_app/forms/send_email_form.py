from django import forms
from django.utils import timezone
from ..models import Student, User
from ..src import EmailMessage

import logging
logger = logging.getLogger(__name__)


class SendEmailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        is_super = False
        if 'is_super' in kwargs:
            is_super = kwargs.get('is_super', False)
            kwargs.pop('is_super')
        super().__init__(*args, **kwargs)
        choices = [('board', 'Board'), ('staff', 'Staff'), ('current members', 'Current Members'), ('joad', 'JOAD')]
        if is_super:
            # choices.append(('all members', 'All Members'))
            choices.append(('students', 'Students that have attended'))
        self.fields['include_days'] = forms.IntegerField(max_value=1000, min_value=0, initial=90, required=False)
        self.fields['recipients'] = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple())
        self.fields['subject'] = forms.CharField(initial='Message from Woodley Park Archers')
        self.fields['subject'].widget.attrs.update({'class': 'form-control m-2'})
        self.fields['message'] = forms.CharField(widget=forms.Textarea)
        self.fields['message'].widget.attrs.update({'cols': 60, 'rows': 8, 'class': 'form-control m-2'})
