from django import forms
from django.forms import TextInput

from src import MyModelForm
from ..models import Student
import logging
logger = logging.getLogger(__name__)


class StudentForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        # def __init__(self, *args, **kwargs):
        #     super.__init__(*args, **kwargs)

        model = Student
        disabled_fields = []
        hidden_fields = []
        optional_fields = ['email', 'safety_class']
        required_fields = ['first_name', 'last_name', 'dob']
        fields = optional_fields + hidden_fields + disabled_fields + required_fields

    def __init__(self, *args, **kwargs):
        student_is_user = kwargs.get('student_is_user', False)
        if 'student_is_user' in kwargs:
            kwargs.pop('student_is_user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['dob'].widget.attrs.update({'placeholder': 'Date of Birth YYYY-MM-DD'})
        self.fields['dob'].error_messages = {'required': '*', 'invalid': "Enter a valid date in YYYY-MM-DD format"}
        self.fields['safety_class'].widget.attrs.update({'placeholder': 'Safety Class YYYY-MM-DD'})
        self.fields['safety_class'].error_messages = {'required': '*', 'invalid': "Enter a valid date in YYYY-MM-DD format"}
        if student_is_user:
            self.fields['email'].widget.attrs.update({'disabled': 'disabled'})
        else:
            self.fields['email'].widget.attrs.update({'placeholder': 'Email (optional)'})

        # exclude = ['student_family', 'user']
        # widgets = {'first_name': TextInput(attrs={'placeholder': 'First Name', 'autocomplete': 'off',
        #                                           'class': "form-control m-2 member-required"}),
        #            'last_name': TextInput(attrs={'placeholder': 'Last Name', 'autocomplete': 'off',
        #                                          'class': "form-control m-2 member-required"}),
        #            'dob': TextInput(attrs={'placeholder': 'Date of Birth YYYY-MM-DD', 'autocomplete': 'off',
        #                                          'class': 'form-control m-2 member-required',
        #                                          'data-error-msg': "Please enter date in format YYYY-MM-DD"}),
        #            'safety_class': TextInput(attrs={'placeholder': 'Safety Class YYYY-MM-DD', 'autocomplete': 'off',
        #                                             'class': 'form-control m-2',
        #                                             'data-error-msg': "Please enter date in format YYYY-MM-DD"}),
        #            }


