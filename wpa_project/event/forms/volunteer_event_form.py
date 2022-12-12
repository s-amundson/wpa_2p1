from django import forms
from django.utils import timezone
from django.db.models import Count

from src.model_form import MyModelForm
from ..models import Event, VolunteerEvent
from payment.src import EmailMessage, RefundHelper
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
        d = timezone.datetime.now()
        d = timezone.datetime.now().replace(year=d.year, month=d.month, day=d.day, hour=16, minute=0, second=0)
        self.fields['event_date'] = forms.DateTimeField(initial=d)
        self.fields['state'] = forms.ChoiceField(choices=choices(Event.event_states))
    #     for student in students:
    #         self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
    #             attrs={'class': "m-2 student-check"}), required=False,
    #             label=f'{student.first_name} {student.last_name}', initial=True)
    #     # self.fields['session'].queryset = Session.objects.filter(state='open').order_by('start_date')
    #     self.student_count = len(students)
    #
    # def get_boxes(self):
    #     for field_name in self.fields:
    #         if field_name.startswith('student_'):
    #             yield self[field_name]
