import logging
from src.model_form import MyModelForm
from django.utils import datetime_safe, timezone

from ..models import Minutes
from membership.models import Member

logger = logging.getLogger(__name__)


class MinutesForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = Minutes
        exclude = []
        hidden_fields = ['minutes_text']
        optional_fields = ['meeting_date', 'start_time', 'attending', 'memberships', 'balance',
                           'discussion', 'end_time']
        fields = optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        super().__init__(*args, **kwargs)
        self.fields['meeting_date'].initial = datetime_safe.date.today()
        self.fields['memberships'].initial = len(Member.objects.filter(expire_date__gt=timezone.now()))
        self.fields['start_time'].initial = ''
