from django import forms

from ..models import StudentFamily

import logging
logger = logging.getLogger(__name__)


class StudentFamilyRegistrationForm(forms.ModelForm):

    class Meta:
        model = StudentFamily
        fields = ('street', 'city',  'state', 'post_code', 'phone')
        widgets = {'street': forms.TextInput(attrs={'placeholder': 'Street', 'autocomplete': 'off',
                                              'class': "form-control not_empty"}),
                   'city': forms.TextInput(attrs={'placeholder': 'City', 'autocomplete': 'off',
                                            'class': "form-control not_empty"}),
                   'state': forms.TextInput(attrs={'placeholder': 'State', 'autocomplete': 'off',
                                             'class': "form-control not_empty"}),
                   'post_code': forms.TextInput(attrs={'placeholder': 'Zip', 'autocomplete': 'off',
                                                 'class': "form-control not_empty"}),
                   'phone': forms.TextInput(attrs={'placeholder': 'Phone', 'autocomplete': 'off',
                                             'class': "form-control not_empty"})}