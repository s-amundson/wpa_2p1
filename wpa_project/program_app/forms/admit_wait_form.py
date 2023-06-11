from django import forms

from event.models import Registration
from ..tasks import charge_group
import logging

logger = logging.getLogger(__name__)


class AdmitWaitForm(forms.Form):

    def __init__(self, *args, **kwargs):
        if 'event' in kwargs:
            self.event = kwargs.pop('event')
        else:
            self.event = None
        if 'family' in kwargs:
            self.family = kwargs.pop('family')
        else:
            self.family = None
        super().__init__(*args, **kwargs)
        self.refund_errors = []
        if self.event:
            self.registrations = Registration.objects.filter(event=self.event, pay_status='waiting')
            if self.family:
                self.registrations = self.registrations.filter(student__in=self.family.student_set.all())
            for reg in self.registrations.order_by('student__last_name', 'student__first_name'):
                self.fields[f'admit_{reg.id}'] = forms.BooleanField(
                    widget=forms.CheckboxInput(attrs={'class': "m-2 admit"}),
                    required=False,
                    initial=False,
                    label=f'{reg.student.first_name } {reg.student.last_name}')

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('admit_'):
                yield self[field_name]

    def process_admission(self):
        reg_list = []
        for k, v in self.cleaned_data.items():
            if k[:6] == 'admit_' and v:
                reg_list.append(int(k.split('_')[1]))
        # logger.debug(self.registrations.filter(id__in=reg_list))
        logger.warning(reg_list)
        charge_group.delay(reg_list)
        return True
