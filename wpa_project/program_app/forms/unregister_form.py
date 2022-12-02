from django import forms
from django.utils import timezone
from django.db.models import Count

from ..src import ClassRegistrationHelper
from payment.src import EmailMessage, RefundHelper
from ..models import BeginnerClass, ClassRegistration
from ..tasks import update_waiting
import logging

logger = logging.getLogger(__name__)


class BooleanField(forms.BooleanField):
    def __init__(self, reg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reg = reg

    def get_bound_field(self, form, field_name):
        bf = RegBoundField(form, self, field_name)
        d = timezone.localtime(self.reg.beginner_class.event.event_date, timezone.get_current_timezone())
        bf.bc_id = self.reg.beginner_class.id
        bf.class__cost = self.reg.beginner_class.event.cost_standard
        bf.class_date_string = f'{d.strftime("%B %d, %Y %I %p")} ({self.reg.beginner_class.class_type})'
        bf.class__state = self.reg.beginner_class.event.state
        bf.student_string = f'{self.reg.student.first_name} {self.reg.student.last_name}'
        bf.pay_status_string = self.reg.pay_status
        bf.reg_id = self.reg.id
        return bf


class RegBoundField(forms.BoundField):  # pragma: no cover
    @property
    def bcid(self):
        return self.bc_id
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
        else:  # pragma: no cover
            self.family = None
        super().__init__(*args, **kwargs)
        self.template_name = 'program_app/forms/unregister.html'
        self.refund_errors = []
        if self.family:
            self.registrations = ClassRegistration.objects.filter(beginner_class__event__event_date__gte=timezone.now(),
                                                                  student__in=self.family.student_set.all())
            self.registrations = self.registrations.exclude(pay_status__in=['refund donated', 'refunded', 'canceled'])
            self.can_refund = False
            for reg in self.registrations:
                f = BooleanField(reg, widget=forms.CheckboxInput(attrs={'class': f"m-2 unreg {reg.pay_status}"}),
                                 required=False, initial=False)
                f.beginner_class = str(reg.beginner_class.id)
                f.class_date = reg.beginner_class.event.event_date
                f.pay_status = reg.pay_status
                if reg.beginner_class.event.state in reg.beginner_class.event.event_states[4:]:  # class closed
                    # f.widget.attrs.update({'disabled': 'disabled'})
                    f.label = '(no refund)'
                else:
                    self.can_refund = True
                    f.label = ''
                reg.check = self.fields[f'unreg_{reg.id}'] = f
        self.fields['donation'] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': "m-2"}), required=False,
                                                     initial=False, label='Donate refund to WPA')

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('unreg_'):  # pragma: no cover
                yield self[field_name]

    def process_refund(self, user, student_family):
        logging.warning(self.cleaned_data)
        class_list = []
        for k, v in self.cleaned_data.items():
            if k[:5] == 'unreg' and v:
                # logging.debug(k.split('_'))
                class_list.append(int(k.split('_')[1]))
        logging.warning(class_list)
        cr = ClassRegistration.objects.filter(
            id__in=class_list,
            student__in=student_family.student_set.all())
        logging.warning(cr)
        if not len(cr):  # no registrations found
            return True
        not_refundable = cr.filter(
            beginner_class__event__event_date__lt=timezone.now() + timezone.timedelta(hours=24),
            beginner_class__event__state__in=BeginnerClass.class_states[:5])
        not_refundable.update(pay_status='canceled')
        cr = cr.filter(beginner_class__event__event_date__gte=timezone.now() + timezone.timedelta(hours=24),
                       beginner_class__event__state__in=BeginnerClass.class_states[:4])
        logging.warning(cr)
        # if not user.is_board:
        #     cr = cr.filter(
        refund = RefundHelper()
        error_count = 0
        for ikey in cr.values('idempotency_key', 'pay_status').annotate(ik_count=Count('idempotency_key')).order_by():
            logging.debug(ikey)
            icr = cr.filter(idempotency_key=ikey['idempotency_key'])
            cost = icr[0].beginner_class.event.cost_standard
            if ikey['pay_status'] in ['start', 'waiting']:
                icr.update(pay_status='canceled')
                continue
            elif ikey['pay_status'] == 'paid' and self.cleaned_data['donation']:
                square_response = {'status': 'SUCCESS'}

            elif ikey['pay_status'] == 'paid':
                square_response = refund.refund_with_idempotency_key(ikey['idempotency_key'],
                                                                     cost * 100 * ikey['ik_count'])
            logging.debug(square_response)

            if square_response['status'] in ['PENDING', 'SUCCESS']:
                if user.student_set.first().student_family == self.family:
                    EmailMessage().refund_email(user, self.cleaned_data['donation'])
                else:
                    for s in self.family.student_set.all():
                        if s.user is not None:
                            EmailMessage().refund_email(s.user, self.cleaned_data['donation'])
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
                update_waiting.delay(icr[0].beginner_class.id)
            else:
                for r in icr:
                    self.add_error(f'unreg_{r.id}', square_response['error'])
                error_count += 1
        return error_count == 0
