import logging
from src.model_form import MyModelForm
from django.utils import timezone
from django.forms import Form, CharField, DateField, BooleanField

from ..models import Minutes
from membership.models import Member

logger = logging.getLogger(__name__)


class MinutesForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = Minutes
        exclude = []
        hidden_fields = ['minutes_text', 'end_time']
        optional_fields = ['meeting_date', 'attending', 'memberships', 'balance', 'reimbursement_review', 'discussion']
        fields = optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        super().__init__(*args, **kwargs)
        self.fields['memberships'].initial = len(Member.objects.filter(expire_date__gt=timezone.now()))
        self.fields['reimbursement_review'].widget.attrs = {'class': "m-2", }
        for f in self.Meta.fields:
            self.fields[f].widget.attrs['class'] += ' minutes-input'


class MinutesSearchForm(Form):
    search_string = CharField(required=False)
    begin_date = DateField(required=False)
    end_date = DateField(required=False)
    reports = BooleanField(required=False)
    business = BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        minutes = Minutes.objects.all()
        if len(minutes):
            minutes.order_by('meeting_date')
            self.fields['begin_date'].initial = minutes.first().meeting_date
            self.fields['end_date'].initial = minutes.last().meeting_date
