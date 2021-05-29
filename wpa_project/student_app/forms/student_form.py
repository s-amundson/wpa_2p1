from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from django.forms import TextInput

from ..models import Student


class StudentForm(BSModalModelForm):
    dob = forms.DateField(
        error_messages={'invalid': "Enter a valid date in YYYY-MM-DD format"}
    )

    class Meta:
        model = Student
        exclude = ['safety_class', 'student_family']
        widgets = {'first_name': TextInput(attrs={'placeholder': 'First Name', 'autocomplete': 'off',
                                                  'class': "form-control m-2 member-required"}),
                   'last_name': TextInput(attrs={'placeholder': 'Last Name', 'autocomplete': 'off',
                                                 'class': "form-control m-2 member-required"}),
                   'dob': TextInput(attrs={'placeholder': 'Date of Birth YYYY-MM-DD', 'autocomplete': 'off',
                                                 'class': 'form-control m-2 member-required',
                                                 'data-error-msg': "Please enter date in format YYYY-MM-DD"}),
                   }