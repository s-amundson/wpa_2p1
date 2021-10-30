from django.forms import BooleanField, CheckboxInput, RadioSelect
from django.utils.datetime_safe import date
import logging
from src.model_form import MyModelForm
from ..models import Membership, Level
logger = logging.getLogger(__name__)


class MembershipForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Membership
        fields = ['level']
        hidden_fields = []
        optional_fields = []

    def __init__(self, students, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for student in students:
            dob = student.dob
            age = date.today().year - student.dob.year
            self.fields[f'student_{student.id}'] = BooleanField(widget=CheckboxInput(
                attrs={'class': "m-2 student-check", 'age': age}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=False)

        choices = []
        levels = Level.objects.filter(enabled=True)
        for level in levels:
            choices.append((level.id, level.name))
        logging.debug(choices)
        self.fields['level'].widget = RadioSelect(choices=choices)

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]