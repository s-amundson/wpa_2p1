from src import MyModelForm
from django import forms
from django.utils.datetime_safe import date
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import Student
import logging
logger = logging.getLogger(__name__)


class StudentDeleteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)
        self.fields['delete'] = forms.CharField(label='Enter "delete" in order to remove this student')
        self.fields['pk'] = forms.IntegerField(widget=forms.HiddenInput(), initial=self.instance.id)
        self.can_delete = not self.instance.registration_set.filter(
            pay_status__in=['admin', 'paid', 'waiting'], event__event_date__gte=timezone.now()).count()
        logger.warning(self.can_delete)

    def clean(self):
        data = super().clean()
        logger.warning(data)
        student = Student.objects.filter(pk=data['pk']).last()
        logger.warning(student)
        if student is None:
            raise ValidationError("Form Error - Invalid Student")
        if student.registration_set.filter(
                pay_status__in=['admin', 'paid', 'waiting'], event__event_date__gte=timezone.now()).count():
            raise ValidationError("Student has registrations")
        data['pk'] = student
        return data


class StudentForm(MyModelForm):
    class Meta(MyModelForm.Meta):

        model = Student
        disabled_fields = []
        hidden_fields = []
        optional_fields = ['email', 'safety_class']
        required_fields = ['first_name', 'last_name', 'dob']
        fields = optional_fields + hidden_fields + disabled_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dob'].widget = forms.SelectDateWidget(years=range(date.today().year, date.today().year - 100, -1))
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['dob'].label = "Date of Birth"
        self.fields['safety_class'].widget = forms.SelectDateWidget(years=range(date.today().year, 2019, -1))

        if self.instance.user:
            self.fields['email'].widget.attrs.update({'disabled': 'disabled'})
        else:
            self.fields['email'].widget.attrs.update({'placeholder': 'Email (optional)'})
