from django import forms

from src.model_form import MyModelForm
from ..models import Registration, VolunteerEvent
import logging

logger = logging.getLogger(__name__)


class RegistrationForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Registration
        required_fields = ['event']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, students, *args, **kwargs):
        self.cancel_form = kwargs.get('cancel', False)
        self.event_queryset = kwargs.get('event_queryset', None)
        for k in ['cancel', 'event_type', 'event_queryset']:
            if k in kwargs:
                kwargs.pop(k)
        super().__init__(*args, **kwargs)

        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check", 'is_beginner': 'T' if student.safety_class is None else 'F',
                       'dob': f"{student.dob}"}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=True)
        self.student_count = len(students)
        self.description = ''
        # logger.warning(self.initial)
        if self.event_queryset is not None:
            self.fields['event'].queryset = self.event_queryset
        if 'event' in self.initial:
            self.fields['event'].queryset = self.fields['event'].queryset.filter(pk=self.initial['event'])
            ve = VolunteerEvent.objects.filter(event__id=self.initial['event'])
            if len(ve):
                logger.warning(ve.last())
                self.description = ve.last().description
    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]


class RegistrationAdminForm(RegistrationForm):
    def __init__(self, students, *args, **kwargs):
        super().__init__(students, *args, **kwargs)
        self.fields['notes'] = forms.CharField(required=False)
        self.fields['notes'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})
        self.fields['payment'] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=False,
            label=f'Payment',
            initial=False)
        self.fields['student'] = forms.ModelChoiceField(queryset=students.filter(user__isnull=False),
                                                        label='Requesting Student')