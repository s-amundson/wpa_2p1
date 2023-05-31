from django.forms import DateTimeField, ChoiceField
from django.utils import timezone

from src.model_form import MyModelForm
from src.model_helper import choices
from ..models import JoadClass
from event.models import Event

import logging
logger = logging.getLogger(__name__)


class ClassForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = JoadClass
        required_fields = []
        disabled_fields = ['session']
        fields = required_fields + disabled_fields

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_date = self.initial.get('class_date', None)
        if class_date is None:
            class_date = timezone.datetime.combine(session.start_date, timezone.datetime.min.time())
            if not timezone.is_aware(class_date):
                class_date = timezone.make_aware(class_date)
            for c in session.joadclass_set.all():
                if class_date <= c.event.event_date:
                    class_date = c.event.event_date + timezone.timedelta(days=7)
        self.fields['state'] = ChoiceField(choices=choices(Event.event_states))
        self.fields['class_date'] = DateTimeField(initial=class_date)
        self.fields['class_date'].widget.attrs.update({'class': 'form-control m-2'})
