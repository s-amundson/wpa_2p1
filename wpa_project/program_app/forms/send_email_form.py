from django import forms

from student_app.forms import SendEmailForm
from ..src import EmailMessage
from student_app.models import User, Student

import logging
logger = logging.getLogger(__name__)


class SendClassEmailForm(SendEmailForm):
    def __init__(self, *args, **kwargs):
        self.beginner_class = kwargs.pop('beginner_class')
        super().__init__(*args, **kwargs)
        self.fields.pop('recipients')
        self.fields['attending_only'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check"}), required=False)

    def send_message(self):
        em = EmailMessage()
        users = User.objects.filter(is_active=True)
        class_registrations = self.beginner_class.event.registration_set.filter(pay_status__in=['paid', 'admin'])
        logger.warning(users.filter(registration__in=class_registrations))
        if self.cleaned_data['attending_only']:
            class_registrations = class_registrations.filter(attended=True)
        em.send_mass_message(users.filter(registration__in=class_registrations),
                         self.cleaned_data['subject'],
                         self.cleaned_data['message'])
