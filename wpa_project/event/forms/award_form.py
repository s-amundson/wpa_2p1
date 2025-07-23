import math
import random
from django import forms
from django.utils import timezone

from ..models import VolunteerAward
import logging

logger = logging.getLogger(__name__)


class AwardForm(forms.ModelForm):
    class Meta:
        model = VolunteerAward
        required_fields = ['events', 'award']
        optional_fields = ['received', 'student', 'description']
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
        if self.instance.id:
            self.fields['student'].disabled = True
            self.fields['events'].disabled = True
        else:
            self.fields['student'].widget = forms.HiddenInput()
        self.fields['student'].label = 'Volunteer'

        self.fields['events'].queryset = self.fields['events'].queryset.filter(
            event_date__lte=timezone.now(),
            event_date__gte=(timezone.now() - timezone.timedelta(days=90))).order_by('-event_date')
        self.fields['events'].widget.attrs['size'] = 12

    def clean(self):
        cleaned_data = super().clean()
        logger.warning(cleaned_data)
        if cleaned_data['student'] is None:

            student_list = []
            for event in cleaned_data['events']:
                for record in event.volunteerrecord_set.all():
                    points = math.floor(record.volunteer_points)
                    for n in range(points):
                        if not record.student.user.has_perm('student_app.board'):
                            student_list.append(record.student)
            logger.warning(student_list)
            if len(student_list):
                cleaned_data['student'] = random.choice(student_list)
            else:
                self.add_error('events', 'No eligible volunteers for this event')
