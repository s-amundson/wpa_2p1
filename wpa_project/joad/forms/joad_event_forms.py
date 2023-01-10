from django.utils import timezone
from django import forms
from datetime import timedelta

from src.model_form import MyModelForm
from src.model_helper import choices
from ..models import EventRegistration, JoadEvent
from event.models import Event
from payment.models import CostsModel
from program_app.src import UpdatePrograms
from student_app.models import Student

import logging
logger = logging.getLogger(__name__)


class EventRegistrationForm(forms.ModelForm):

    class Meta(MyModelForm.Meta):
        model = EventRegistration
        required_fields = ['joad_event']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, user, *args, **kwargs):
        # if "instance"
        super().__init__(*args, **kwargs)
        logging.warning(kwargs)
        # logging.warning(self.initial['event'].id)
        if user.is_board:
            students = Student.objects.all()
        else:
            students = Student.objects.get(user=user).student_family.student_set.all()
        students = students.filter(is_joad=True)
        d = timezone.localdate(timezone.now())
        old = d.replace(year=d.year - 21)
        young = d.replace(year=d.year - 9)
        students = students.filter(dob__gt=old).filter(dob__lte=young).order_by('last_name')

        # students = list(students.values())
        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check"}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=True)
        logging.warning(JoadEvent.objects.filter(event__state='open').order_by('event__event_date'))
        self.fields['joad_event'].queryset = JoadEvent.objects.filter(event__state='open').order_by('event__event_date')
        self.fields['joad_event'].default = self.initial['joad_event']
        self.student_count = len(students)

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]


class JoadEventForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = JoadEvent
        required_fields = ['event_type', 'student_limit', 'pin_cost']
        fields = required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        costs = CostsModel.objects.filter(name='Pin Shoot', enabled=True).first()
        logging.debug(costs)
        if costs is not None:
            self.initial['cost'] = costs.standard_cost

        pin_cost = CostsModel.objects.filter(name='JOAD Pin', enabled=True).first()
        if pin_cost is not None:
            self.initial['pin_cost'] = pin_cost.standard_cost
        logging.debug(self.initial)
        logging.warning(self.instance.id)
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
