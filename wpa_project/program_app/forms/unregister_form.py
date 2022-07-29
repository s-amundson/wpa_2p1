from django import forms
from django.utils import timezone
from django.db.models import Q
from ..models import BeginnerClass, ClassRegistration
import logging

logger = logging.getLogger(__name__)


class BooleanField(forms.BooleanField):
    def __init__(self, reg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reg = reg

    def get_bound_field(self, form, field_name):
        bf = RegBoundField(form, self, field_name)
        # bf.reg = forms.model_to_dict(self.reg)
        d = timezone.localtime(self.reg.beginner_class.class_date, timezone.get_current_timezone())
        bf.class_date_string = f'{d.strftime("%B %d, %Y %I %p")} ({self.reg.beginner_class.class_type})'
        bf.class__state = self.reg.beginner_class.state
        bf.student_string = f'{self.reg.student.first_name} {self.reg.student.last_name}'
        bf.pay_status_string = self.reg.pay_status
        bf.reg_id = self.reg.id
        return bf


class RegBoundField(forms.BoundField):
    @property
    def class_date(self):
        return self.class_date_string

    @property
    def class_state(self):
        return self.class__state

    @property
    def pay_status(self):
        return self.pay_status_string

    @property
    def reg(self):
        return self.reg_id

    @property
    def student(self):
        return self.student_string


class UnregisterForm(forms.Form):

    def __init__(self, *args, **kwargs):

        if 'family' in kwargs:
            self.family = kwargs.pop('family')
        else:
            self.family = None
        super().__init__(*args, **kwargs)

        if self.family:
            self.registrations = ClassRegistration.objects.filter(beginner_class__class_date__gte=timezone.now())
            for reg in self.registrations:
                f = BooleanField(reg, widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=False, initial=False)
                f.class_date = reg.beginner_class.class_date
                f.pay_status = reg.pay_status
                reg.check = self.fields[f'unreg_{reg.id}'] = f

