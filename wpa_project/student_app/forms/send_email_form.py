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
        # self.fields['returning'] = forms.BooleanField(
        #     widget=forms.CheckboxInput(attrs={'class': "m-2"}),
        #     label='Returning Students Only',
        #     required=False)
        self.fields['include_days'] = forms.IntegerField(max_value=1000, min_value=0, initial=90, required=False)
        # self.fields['recipients'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect())
        self.fields['recipients'] = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple())
        self.fields['subject'] = forms.CharField(initial='Message from Woodley Park Archers')
        self.fields['subject'].widget.attrs.update({'class': 'form-control m-2'})
        self.fields['message'] = forms.CharField(widget=forms.Textarea)
        self.fields['message'].widget.attrs.update({'cols': 60, 'rows': 8, 'class': 'form-control m-2'})

    def send_message(self):
        logger.warning(self.cleaned_data['recipients'])
        em = EmailMessage()
        em.bcc = []
        users = User.objects.filter(is_active=True)
        if 'board' in self.cleaned_data['recipients']:
            em.bcc_from_users(users.filter(is_board=True), append=True)
        if 'staff' in self.cleaned_data['recipients']:
            em.bcc_from_users(users.filter(is_staff=True), append=True)
        if 'current members' in self.cleaned_data['recipients']:
            em.bcc_from_users(users.filter(is_member=True), append=True)
        if 'joad' in self.cleaned_data['recipients']:
            students = Student.objects.filter(is_joad=True)
            em.bcc_from_students(students, append=True)
        # elif self.cleaned_data['recipients'] == 'all members':
        #     em.bcc_from_users(users.filter(is_staff=True))
        if 'students' in self.cleaned_data['recipients']:
            days = self.cleaned_data.get('include_days', 0)
            if days is None:
                days = 90
            d = timezone.now() - timezone.timedelta(days=days)
            students = Student.objects.filter(registration__event__event_date__gte=d, registration__attended=True)
            logger.warning(students)
            em.bcc_from_students(students, append=True)
        # else:  # pragma no cover
        #     logging.debug('return')
        #     return
        logger.warning(len(em.bcc))
        if len(em.bcc):
            em.send_message(self.cleaned_data['subject'], self.cleaned_data['message'])
