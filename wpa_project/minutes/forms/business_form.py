import logging
from django.forms import ModelForm, BooleanField

from ..models import Business, BusinessUpdate

logger = logging.getLogger(__name__)


class BusinessForm(ModelForm):
    resolved_bool = BooleanField(required=False, initial=False)

    class Meta:
        model = Business
        disabled_fields = ['added_date']
        hidden_fields = ['minutes', ]
        optional_fields = ['business', 'resolved', 'resolved_bool']
        fields = optional_fields + hidden_fields + disabled_fields

    def __init__(self, *args, **kwargs):
        old_business = kwargs.get('old', False)
        if 'old' in kwargs:
            kwargs.pop('old')

        super().__init__(*args, **kwargs)
        logging.debug(self.initial)
        self.auto_id = 'business_%s'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        for f in self.Meta.disabled_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'disabled': 'disabled'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['business'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})
        if old_business: # if true; disable the input so it can't be modified
            self.fields['business'].widget.attrs.update({'class': 'form-control m-2', 'disabled': 'disabled'})
        if self.initial.get('resolved', None) is not None:
            self.fields['resolved_bool'].initial = True

        else:
            self.fields['resolved_bool'].initial = False
        self.fields['resolved_bool'].widget.attrs.update({'class': "m-2 resolved-check"})


class BusinessUpdateForm(ModelForm):

    class Meta:
        model = BusinessUpdate
        disabled_fields = ['update_date']
        hidden_fields = ['business', ]
        optional_fields = ['update_text', ]
        fields = optional_fields + hidden_fields + disabled_fields

    def __init__(self, *args, **kwargs):
        old_update = kwargs.get('old', False)
        if 'old' in kwargs:
            kwargs.pop('old')
        super().__init__(*args, **kwargs)
        self.auto_id = 'update_%s'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        for f in self.Meta.disabled_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'disabled': 'disabled'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['update_text'].widget.attrs.update({'cols': 60, 'rows': 3, 'class': 'form-control m-2 update'})
        if old_update:
            self.fields['update_text'].widget.attrs.update({'disabled': 'disabled'})
