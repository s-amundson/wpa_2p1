from django import forms

import logging

logger = logging.getLogger(__name__)


class ClassSignInForm(forms.Form):

    def __init__(self, *args, **kwargs):
        of_age = kwargs.get('of_age', False)
        if 'of_age' in kwargs:
            kwargs.pop('of_age')
        super().__init__(*args, **kwargs)

        self.fields['signature'] = forms.CharField(widget=forms.HiddenInput())

        for f in ['sig_last_name', 'sig_first_name']:
            self.fields[f] = forms.CharField()
            if of_age:
                self.fields[f].required = False
                self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'readonly': 'readonly'})
            else:
                self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
