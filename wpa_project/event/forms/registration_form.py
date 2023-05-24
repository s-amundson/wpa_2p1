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
        self.students = students
        self.event_type = kwargs.get('event_type', 'class')
        for k in ['cancel', 'event_type', 'event_queryset']:
            if k in kwargs:
                kwargs.pop(k)
        super().__init__(*args, **kwargs)
        if self.event_type == 'class':
            self.fields[f'terms'] = forms.BooleanField(widget=forms.CheckboxInput(
                        attrs={'class': "m-2"}), required=True,
                        label=f'I agree to the terms', initial=False)

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


class RegistrationForm2(MyModelForm):
    # this is used in formsets
    class Meta(MyModelForm.Meta):
        model = Registration
        required_fields = ['student']
        optional_fields = ['comment']
        fields = optional_fields + required_fields

    def __init__(self, students, *args, **kwargs):
        self.cancel_form = kwargs.get('cancel', False)
        self.event_queryset = kwargs.get('event_queryset', None)
        self.students = students

        self.is_staff = kwargs.get('is_staff', False)
        event_type = kwargs.get('event_type', 'class')
        for k in ['cancel', 'is_staff', 'event_type']:
            if k in kwargs:
                kwargs.pop(k)
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.students
        self.fields['student'].widget = forms.HiddenInput()
        self.initial_student = None

        label = ''
        is_beginner = 'F'
        if 'initial' in kwargs:
            label = kwargs['initial'].get('student', '')
            self.initial_student = kwargs['initial'].get('student', None)
            is_beginner = 'T' if self.initial_student.safety_class is None else 'F'

        # the student-check class and the is_beginner attribute is for class_registration.js to uncheck students
        # based on class type
        self.fields['register'] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs={'class': "m-2 student-check", 'is_beginner': is_beginner}),
            required=False,
            initial=True,
            label=label)

        if event_type == 'work':
            self.fields['heavy'] = forms.BooleanField(widget=forms.CheckboxInput(
                    attrs={'class': "m-2", }), required=False, initial=False)
        self.empty_permitted = False
