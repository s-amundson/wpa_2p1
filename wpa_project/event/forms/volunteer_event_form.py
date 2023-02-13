from django import forms
from django.utils import timezone

from src.model_form import MyModelForm
from ..models import Event, VolunteerEvent
from src.model_helper import choices
import logging

logger = logging.getLogger(__name__)


class VolunteerEventForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = VolunteerEvent
        required_fields = ['volunteer_limit', 'description']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        d = timezone.now()
        d = timezone.now().replace(year=d.year, month=d.month, day=d.day, hour=16, minute=0, second=0)
        self.fields['event_date'] = forms.DateTimeField(initial=d)
        self.fields['state'] = forms.ChoiceField(choices=choices(Event.event_states))
        if self.instance.id:
            self.fields['event_date'].initial = self.instance.event.event_date
            self.fields['state'].initial = self.instance.event.state
