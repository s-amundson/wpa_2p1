from django import forms
from django.utils import timezone
from django.db.models import Count

from ..src import ClassRegistrationHelper
from payment.src import EmailMessage, RefundHelper
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
        bf.class__cost = self.reg.beginner_class.cost
        bf.class_date_string = f'{d.strftime("%B %d, %Y %I %p")} ({self.reg.beginner_class.class_type})'
        bf.class__state = self.reg.beginner_class.state
        bf.student_string = f'{self.reg.student.first_name} {self.reg.student.last_name}'
        bf.pay_status_string = self.reg.pay_status
        bf.reg_id = self.reg.id
        return bf


class RegBoundField(forms.BoundField):
    @property
    def class_cost(self):
        return self.class__cost

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
        self.template_name = 'program_app/forms/unregister.html'
        logging.debug(self.family)
        self.refund_errors = []
        if self.family:
            self.registrations = ClassRegistration.objects.filter(beginner_class__class_date__gte=timezone.now(),
                                                                  student__in=self.family.student_set.all())
            self.registrations = self.registrations.exclude(pay_status__in=['refund donated', 'refunded', 'canceled'])
            self.can_unregister = False
            for reg in self.registrations:
                f = BooleanField(reg, widget=forms.CheckboxInput(attrs={'class': "m-2 unreg"}), required=False,
                                 initial=False)
                f.class_date = reg.beginner_class.class_date
                f.pay_status = reg.pay_status
                if reg.beginner_class.state in reg.beginner_class.class_states[3:]:  # class closed
                    f.widget.attrs.update({'disabled': 'disabled'})
                    f.label = 'class closed'
                else:
                    self.can_unregister = True
                    f.label = ''
                reg.check = self.fields[f'unreg_{reg.id}'] = f
        self.fields['donation'] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=False,
                                                     initial=False, label='Donate refund to WPA')

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('unreg_'):
                yield self[field_name]

    def process_refund(self, user, student_family):
        class_list = []
        for k, v in self.cleaned_data.items():
            if k[:5] == 'unreg' and v:
                # logging.debug(k.split('_'))
                class_list.append(int(k.split('_')[1]))
        # logging.debug(class_list)
        cr = ClassRegistration.objects.filter(
            id__in=class_list,
            beginner_class__class_date__gte=timezone.now() + timezone.timedelta(hours=24),
            beginner_class__state__in=BeginnerClass.class_states[:3])  # not class closed
        cr = cr.filter()
        if not user.is_board:
            cr = cr.filter(student__in=student_family.student_set.all())
        refund = RefundHelper()
        error_count = 0
        for ikey in cr.values('idempotency_key', 'pay_status').annotate(ik_count=Count('idempotency_key')).order_by():
            icr = cr.filter(idempotency_key=ikey['idempotency_key'])
            cost = icr[0].beginner_class.cost
            if ikey['pay_status'] == 'paid' and self.cleaned_data['donation']:
                square_response = {'status': 'SUCCESS'}

            elif ikey['pay_status'] == 'paid':
                square_response = refund.refund_with_idempotency_key(ikey['idempotency_key'],
                                                                     cost * 100 * ikey['ik_count'])

            if square_response['status'] in ['PENDING', 'SUCCESS']:
                EmailMessage().refund_email(user, self.cleaned_data['donation'])
                crh = ClassRegistrationHelper()
                for r in icr:
                    if ikey['pay_status'] == 'paid' and self.cleaned_data['donation']:
                        r.pay_status = 'refund donated'
                    elif ikey['pay_status'] in ['paid', 'refunded']:
                        r.pay_status = 'refunded'
                    else:
                        r.pay_status = 'canceled'
                    r.save()
                    crh.update_class_state(r.beginner_class)
            else:
                for r in icr:
                    self.add_error(f'unreg_{r.id}', square_response['error'])
                error_count += 1
        return error_count == 0
