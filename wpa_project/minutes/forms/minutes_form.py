import logging
from django.forms import ModelForm
from django.utils import datetime_safe, timezone

from ..models import Minutes
from membership.models import Member

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
