import logging
from django.forms import ModelForm, BooleanField
from django.utils import datetime_safe, timezone

from ..models import Member, Minutes, MinutesBusiness, MinutesBusinessUpdate, MinutesReport

logger = logging.getLogger(__name__)


class MinutesForm(ModelForm):

    class Meta:
        model = Minutes
        exclude = []
        optional_fields = ['meeting_date', 'start_time', 'attending', 'minutes_text', 'memberships', 'balance',
                           'discussion', 'end_time']

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        super().__init__(*args, **kwargs)

        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            if not edit:
                self.fields[f].widget.attrs.update({'disabled': 'disabled'})
        self.fields['meeting_date'].initial = datetime_safe.date.today()
        self.fields['memberships'].initial = len(Member.objects.filter(expire_date__gt=timezone.now()))
        self.fields['start_time'].initial = ''


class MinutesBusinessForm(ModelForm):
    resolved_bool = BooleanField(required=False, initial=False)

    class Meta:
        model = MinutesBusiness
        disabled_fields = ['added_date']
        hidden_fields = ['minutes', ]
        optional_fields = ['business', 'resolved', 'resolved_bool']
        fields = optional_fields + hidden_fields + disabled_fields

    def __init__(self, *args, **kwargs):
        old_business = kwargs.get('old', False)
        if 'old' in kwargs:
            kwargs.pop('old')
        if 'initial' in kwargs:
            logging.debug('initial')

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



class MinutesBusinessUpdateForm(ModelForm):

    class Meta:
        model = MinutesBusinessUpdate
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


class MinutesReportForm(ModelForm):

    class Meta:
        model = MinutesReport
        optional_fields = ['report']
        hidden_fields = ['minutes', 'owner']
        fields = optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        super().__init__(*args, **kwargs)
        self.auto_id = 'report_%s'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['report'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})
        if not edit:
            self.fields['report'].widget.attrs.update({'disabled': 'disabled'})

