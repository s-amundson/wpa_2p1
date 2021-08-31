from django.forms import ModelForm, IntegerField
from django.utils import datetime_safe, timezone

from ..models import MemberModel, MinutesModel, MinutesBusinessModel, MinutesReportModel


class MinutesForm(ModelForm):

    class Meta:
        model = MinutesModel
        exclude = []
        optional_fields = ['meeting_date', 'start_time', 'attending', 'minutes_text', 'memberships', 'balance',
                           'discussion', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.Meta.optional_fields:
            self.fields[f].required = False
        self.fields['meeting_date'].initial = datetime_safe.date.today()
        self.fields['memberships'].initial = len(MemberModel.objects.filter(expire_date__gt=timezone.now()))


class MinutesBusinessForm(ModelForm):
    class Meta:
        model = MinutesBusinessModel
        disabled_fields = ['added_date']
        hidden_fields = ['minutes']
        optional_fields = ['business', 'resolved']

        fields = optional_fields + hidden_fields + disabled_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_id = 'business_%s'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
        for f in self.Meta.disabled_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'disabled': 'disabled'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['business'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})

class MinutesReportForm(ModelForm):

    class Meta:
        model = MinutesReportModel
        optional_fields = ['report']
        hidden_fields = ['minutes', 'owner']
        fields = optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_id = 'report_%s'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['report'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})

