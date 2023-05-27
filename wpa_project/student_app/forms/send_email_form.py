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
            choices.append(('students', 'All Students'))
        self.fields['returning'] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs={'class': "m-2"}),
            label='Returning Students Only',
            required=False)
        self.fields['include_days'] = forms.IntegerField(max_value=90, min_value=0, initial=0, required=False)
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
        elif self.cleaned_data['recipients'] == 'staff':
            em.bcc_from_users(users.filter(is_staff=True))
        elif self.cleaned_data['recipients'] == 'current members':
            em.bcc_from_users(users.filter(is_member=True))
        elif self.cleaned_data['recipients'] == 'joad':
            students = Student.objects.filter(is_joad=True)
            em.bcc_from_students(students)
        # elif self.cleaned_data['recipients'] == 'all members':
        #     em.bcc_from_users(users.filter(is_staff=True))
        elif self.cleaned_data['recipients'] == 'students':
            days = self.cleaned_data.get('include_days', 0)
            if days is None:
                days = 90
            d = timezone.now() - timezone.timedelta(days=days)
            students = Student.objects.filter(registration__event__event_date__gte=d, registration__attended=True)
            logger.warning(students)
            em.bcc_from_students(students)
        else:  # pragma no cover
            logging.debug('return')
            return
        em.send_message(self.cleaned_data['subject'], self.cleaned_data['message'])
