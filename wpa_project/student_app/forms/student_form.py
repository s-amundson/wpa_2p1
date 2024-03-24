from src import MyModelForm
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import Student, StudentFamily
from event.models import Registration
import logging
logger = logging.getLogger(__name__)


class StudentDeleteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.delete_family = False
        if 'delete_family' in kwargs:
            self.delete_family = kwargs.pop('delete_family')
        super().__init__(*args, **kwargs)

        self.fields['pk'] = forms.IntegerField(widget=forms.HiddenInput(), initial=self.instance.id)
        self.multi_user = False
        if self.delete_family:
            registrations = Registration.objects.filter(
                student__student_family=self.instance,
                pay_status__in=['admin', 'paid', 'waiting'],
                event__event_date__gte=timezone.now()
            )
            logger.warning(registrations)
            self.can_delete = not registrations.count()
            self.multi_user = self.instance.student_set.filter(user__isnull=False).count() > 1
        else:
            self.can_delete = not self.instance.registration_set.filter(
                pay_status__in=['admin', 'paid', 'waiting'], event__event_date__gte=timezone.now()).count()
            if self.instance.user:
                self.fields['removal_choice'] = forms.ChoiceField(
                    choices=(('delete', "Delete student's account"),
                             ('remove', 'Remove student from account without deleting')),
                    initial='remove'
                )
        self.fields['delete'] = forms.CharField(label='Enter "delete" in order to remove this student')
        logger.warning(self.can_delete)
        logger.warning(self.multi_user)

    def clean(self):
        data = super().clean()
        logger.warning(data)
        if self.delete_family:
            sf = StudentFamily.objects.filter(pk=data['pk']).last()
            if not self.can_delete:
                raise ValidationError("Student has registrations")
            data['pk'] = sf

        else:
            student = Student.objects.filter(pk=data['pk']).last()
            logger.warning(student)
            if student is None:
                raise ValidationError("Form Error - Invalid Student")
            if student.registration_set.filter(
                    pay_status__in=['admin', 'paid', 'waiting'], event__event_date__gte=timezone.now()).count():
                raise ValidationError("Student has registrations")
            data['pk'] = student
        return data

    def clean_delete(self):
        data = self.cleaned_data["delete"].strip()
        if not data.lower() in ['remove', 'delete']:
            raise ValidationError("Incorrect verification")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
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
        self.fields['dob'].widget = forms.SelectDateWidget(years=range(timezone.datetime.today().year,
                                                                       timezone.datetime.today().year - 100, -1))
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['dob'].label = "Date of Birth"
        self.fields['safety_class'].widget = forms.SelectDateWidget(years=range(timezone.datetime.today().year, 2019, -1))

        if self.instance.user:
            self.fields['email'].widget.attrs.update({'disabled': 'disabled'})
        else:
            self.fields['email'].widget.attrs.update({'placeholder': 'Email (optional)'})

    # def clean_email(self):
    #     data = self.cleaned_data["email"]
    #     logger.warning(data)
    #     if data is not None:
    #         logger.warning(EmailAddress.objects.filter(email=data))
    #         if EmailAddress.objects.filter(email=data).count():
    #             raise ValidationError("Email in use")
    #
    #     # Always return a value to use as the new cleaned data, even if
    #     # this method didn't change it.
    #     return data
