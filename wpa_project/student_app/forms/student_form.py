from django import forms
from django.forms import TextInput, ModelForm

from ..models import Student
import logging
logger = logging.getLogger(__name__)


class StudentForm(ModelForm):
    dob = forms.DateField(
        error_messages={'invalid': "Enter a valid date in YYYY-MM-DD format"}
    )
    safety_class = forms.DateField(required=False,
        error_messages={'invalid': "Enter a valid date in YYYY-MM-DD format"}
    )


    class Meta:
        model = Student
        exclude = ['student_family', 'user']
        widgets = {'first_name': TextInput(attrs={'placeholder': 'First Name', 'autocomplete': 'off',
                                                  'class': "form-control m-2 member-required"}),
                   'last_name': TextInput(attrs={'placeholder': 'Last Name', 'autocomplete': 'off',
                                                 'class': "form-control m-2 member-required"}),
                   'dob': TextInput(attrs={'placeholder': 'Date of Birth YYYY-MM-DD', 'autocomplete': 'off',
                                                 'class': 'form-control m-2 member-required',
                                                 'data-error-msg': "Please enter date in format YYYY-MM-DD"}),
                   'safety_class': TextInput(attrs={'placeholder': 'Safety Class YYYY-MM-DD', 'autocomplete': 'off',
                                                    'class': 'form-control m-2',
                                                    'data-error-msg': "Please enter date in format YYYY-MM-DD"}),
                   }

