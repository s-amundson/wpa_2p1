from django.forms import BooleanField, CheckboxInput, ModelForm, MultipleChoiceField, RadioSelect
from django.utils.datetime_safe import date
import logging

from ..models import MembershipModel, LevelModel
logger = logging.getLogger(__name__)


class MembershipForm(ModelForm):

    class Meta:
        model = MembershipModel
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
        levels = LevelModel.objects.filter(enabled=True)
        for level in levels:
            choices.append((level.id, level.name))
        logging.debug(choices)
        self.fields['level'].widget = RadioSelect(choices=choices)
        # self.fields['level'].choices = choices
        # for f in self.Meta.fields:
        #     self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        # for f in self.Meta.optional_fields:
        #     self.fields[f].required = False
        # for f in self.Meta.hidden_fields:
        #     self.fields[f].required = False
        #     self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'disabled': 'disabled'})
    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]