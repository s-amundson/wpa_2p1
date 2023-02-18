from django.utils import timezone
from django import forms
from datetime import timedelta

from src.model_form import MyModelForm
from src.model_helper import choices
from ..models import JoadEvent
from event.models import Event
from payment.models import CostsModel
from program_app.src import UpdatePrograms

import logging
logger = logging.getLogger(__name__)


class JoadEventForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = JoadEvent
        required_fields = ['event_type', 'student_limit', 'pin_cost']
        fields = required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        costs = CostsModel.objects.filter(name='Pin Shoot', enabled=True).first()
        logger.debug(costs)
        if costs is not None:
            self.initial['cost'] = costs.standard_cost

        pin_cost = CostsModel.objects.filter(name='JOAD Pin', enabled=True).first()
        if pin_cost is not None:
            self.initial['pin_cost'] = pin_cost.standard_cost
        logger.debug(self.initial)
        logger.warning(self.instance.id)
        self.fields['state'] = forms.ChoiceField(choices=choices(Event.event_states))
        self.fields['cost'] = forms.IntegerField()
        if self.instance and self.instance.event:
            d = self.instance.event.event_date
            self.fields['state'].initial = self.instance.event.state
            self.fields['cost'].initial = self.instance.event.cost_standard
        else:
            d = UpdatePrograms().next_class_day(1) + timedelta(days=14)
            d = timezone.datetime.now().replace(year=d.year, month=d.month, day=d.day, hour=16, minute=0, second=0)
        self.fields['event_date'] = forms.DateTimeField(initial=d)
