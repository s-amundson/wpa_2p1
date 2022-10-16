# from datetime import timedelta
from django import forms
from django.utils import timezone
from ..models import BeginnerClass, ClassRegistration
import logging

logger = logging.getLogger(__name__)


class ClassRegistrationForm(forms.Form):

    def __init__(self, students, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bc = self.get_open_classes(user)
        self.fields['beginner_class'] = forms.ChoiceField(choices=bc)
        self.students = list(students.values())
        self.needs_covid = len(students.filter(covid_vax=False))
        logging.warning(self.needs_covid)
        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check", 'is_beginner': 'T' if student.safety_class is None else 'F',
                       'dob': f"{student.dob}"}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=True)
        if not user.is_board:
            self.fields['terms'] = forms.BooleanField(
                widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=True,
                label=f'I agree to the terms of the AWRL, COVID-19 Policy and the Cancellation Policy',
                initial=False)

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]

    def get_open_classes(self, user):
        date = timezone.now() - timezone.timedelta(hours=6)
        classes = BeginnerClass.objects.filter(class_date__gt=date).order_by('class_date')
        if user.is_board:
            classes = classes.filter(state__in=['open', 'wait', 'full', 'closed'])
        elif user.is_staff:
            classes = classes.filter(state__in=['open', 'wait', 'full'])
        else:
            classes = classes.filter(state__in=['open', 'wait'])
        d = [("", "None")]
        for c in classes:
            cd = timezone.localtime(c.class_date)
            s = cd.strftime("%d %b, %Y %I:%M %p")
            d.append((str(c.id), s))
        return d

    class Meta:
        model = ClassRegistration
        exclude = ['pay_status', 'order_id', 'reg_time']


class ClassRegistrationAdminForm(ClassRegistrationForm):
    def __init__(self, students, user, *args, **kwargs):
        super().__init__(students, user, *args, **kwargs)
        self.fields['notes'] = forms.CharField(required=False)
        self.fields['notes'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})
        self.fields['payment'] = forms.BooleanField(
            widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=False,
            label=f'Payment',
            initial=False)
        self.fields['student'] = forms.ModelChoiceField(queryset=students.filter(user__isnull=False),
                                                        label='Requesting Student')
