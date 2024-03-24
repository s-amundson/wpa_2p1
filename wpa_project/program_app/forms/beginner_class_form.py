from django import forms
from django.utils import timezone

from ..models import BeginnerClass
from src.model_helper import choices

import logging
logger = logging.getLogger(__name__)


class BeginnerClassForm(forms.ModelForm):

    class Meta:
        model = BeginnerClass
        exclude = ['event']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.event:
            default_date = self.instance.event.event_date
            default_state = self.instance.event.state
        else:
            default_date = timezone.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            default_state = 'open'
        # logging.warning(f'date {default_date}, state {default_state}')
        self.fields['class_date'] = forms.DateTimeField(initial=default_date)
        self.fields['cost'] = forms.IntegerField(initial=5)
        self.fields['state'] = forms.ChoiceField(choices=choices(BeginnerClass.class_states),
                                                 initial=default_state)
        self.fields['cancel_message'] = forms.CharField(required=False)
