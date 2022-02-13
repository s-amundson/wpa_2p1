from django.forms import TextInput, CheckboxInput
from django import forms


class SearchColumnsForm(forms.Form):
    first_name = forms.CharField(widget=TextInput(attrs={'placeholder': 'First Name', 'autocomplete': 'off',
                                                  'class': "form-control m-2"}), required=False)
    last_name = forms.CharField(widget=TextInput(attrs={'placeholder': 'Last Name', 'autocomplete': 'off',
                                                         'class': "form-control m-2"}), required=False)
    safety_class = forms.BooleanField(required=False)
    staff = forms.BooleanField(required=False)


class SearchEmailForm(forms.Form):
    email = forms.EmailField(widget=TextInput(attrs={'placeholder': 'Email', 'autocomplete': 'off', 'name': 'email',
                                                     'class': "form-control m-2 email"}))


class SearchNameForm(forms.Form):
    first_name = forms.CharField(widget=TextInput(attrs={'placeholder': 'First Name', 'autocomplete': 'off',
                                                  'class': "form-control m-2 member-required"}))
    last_name = forms.CharField(widget=TextInput(attrs={'placeholder': 'Last Name', 'autocomplete': 'off',
                                                         'class': "form-control m-2 member-required"}))


class SearchPhoneForm(forms.Form):
    phone = forms.CharField(widget=TextInput(attrs={'placeholder': 'Phone', 'autocomplete': 'off',
                                             'class': "form-control m-2 not_empty"}))

