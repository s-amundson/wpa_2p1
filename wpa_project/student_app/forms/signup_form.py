from allauth.account.forms import SignupForm
from django import forms


class SignUpForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['terms'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2"}), required=True, label=f'I agree to the terms.',
                initial=False)
