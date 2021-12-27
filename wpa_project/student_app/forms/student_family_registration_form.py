from django.forms import ModelForm, TextInput

from ..models import StudentFamily


class StudentFamilyRegistrationForm(ModelForm):

    class Meta:
        model = StudentFamily
        fields = ('street', 'city',  'state', 'post_code', 'phone')
        widgets = {'street': TextInput(attrs={'placeholder': 'Street', 'autocomplete': 'off',
                                              'class': "form-control not_empty"}),
                   'city': TextInput(attrs={'placeholder': 'City', 'autocomplete': 'off',
                                            'class': "form-control not_empty"}),
                   'state': TextInput(attrs={'placeholder': 'State', 'autocomplete': 'off',
                                             'class': "form-control not_empty"}),
                   'post_code': TextInput(attrs={'placeholder': 'Zip', 'autocomplete': 'off',
                                                 'class': "form-control not_empty"}),
                   'phone': TextInput(attrs={'placeholder': 'Phone', 'autocomplete': 'off',
                                             'class': "form-control not_empty"})}