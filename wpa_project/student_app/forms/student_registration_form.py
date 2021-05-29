from django.contrib.auth.forms import UserCreationForm
from django.forms import forms, CheckboxInput, BooleanField, ModelForm, TextInput

from ..models import StudentFamily


class StudentRegistrationForm(ModelForm):

    # terms = BooleanField(widget=CheckboxInput(attrs={'class': "form-control m-2 custom-control-input"}),
    #                            required=True)

    class Meta:
        model = StudentFamily
        fields = ('street', 'city',  'state', 'post_code', 'phone')
        widgets = {'street': TextInput(attrs={'placeholder': 'Street', 'autocomplete': 'off',
                                              'class': "form-control m-2 not_empty"}),
                   'city': TextInput(attrs={'placeholder': 'City', 'autocomplete': 'off',
                                            'class': "form-control m-2 not_empty"}),
                   'state': TextInput(attrs={'placeholder': 'State', 'autocomplete': 'off',
                                             'class': "form-control m-2 not_empty"}),
                   'post_code': TextInput(attrs={'placeholder': 'Zip', 'autocomplete': 'off',
                                                 'class': "form-control m-2 not_empty"}),
                   'phone': TextInput(attrs={'placeholder': 'Phone', 'autocomplete': 'off',
                                             'class': "form-control m-2 not_empty"}),}