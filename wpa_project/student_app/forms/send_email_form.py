from django import forms
from django.forms import Form

from ..models import User
from ..src import EmailMessage

import logging
logger = logging.getLogger(__name__)


class SendEmailForm(Form):

    def __init__(self, *args, **kwargs):
        is_super = False
        if 'is_super' in kwargs:
            is_super =  kwargs.get('is_super', False)
            logging.debug(is_super)
            kwargs.pop('is_super')
        super().__init__(*args, **kwargs)
        choices = [('board', 'Board'), ('staff', 'Staff'), ('current members', 'Current Members')]
        if is_super:
            # choices.append(('all members', 'All Members'))
            choices.append(('students', 'All Students'))
        self.fields['recipients'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect())
        self.fields['subject'] = forms.CharField(initial='Message from Woodley Park Archers')
        self.fields['subject'].widget.attrs.update({'class': 'form-control m-2'})
        self.fields['message'] = forms.CharField(widget=forms.Textarea)
        self.fields['message'].widget.attrs.update({'cols': 60, 'rows': 8, 'class': 'form-control m-2'})

    def send_message(self):
        logging.debug(self.cleaned_data['recipients'])
        em = EmailMessage()
        users = User.objects.filter(is_active=True)
        if self.cleaned_data['recipients'] == 'board':
            em.bcc_from_users(users.filter(is_board=True))
            logging.debug(em.bcc)
        elif self.cleaned_data['recipients'] == 'staff':
            em.bcc_from_users(users.filter(is_staff=True))
        elif self.cleaned_data['recipients'] == 'current members':
            em.bcc_from_users(users.filter(is_member=True))
        # elif self.cleaned_data['recipients'] == 'all members':
        #     em.bcc_from_users(users.filter(is_staff=True))
        elif self.cleaned_data['recipients'] == 'students':
            em.bcc_from_users(users)
        else:
            return
        em.send_message(self.cleaned_data['subject'], self.cleaned_data['message'])
