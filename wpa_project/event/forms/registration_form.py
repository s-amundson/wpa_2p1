from django import forms
from django.utils import timezone
from django.db.models import Count

from src.model_form import MyModelForm
from ..models import Registration
from payment.src import EmailMessage, RefundHelper
import logging

logger = logging.getLogger(__name__)


class VolunteerRegistrationForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Registration
        required_fields = ['event']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, students, *args, **kwargs):
        self.cancel_form = kwargs.get('cancel', False)
        if 'cancel' in kwargs:
            kwargs.pop('cancel')
        super().__init__(*args, **kwargs)

        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check"}), required=False,
                label=f'{student.first_name} {student.last_name}', initial=True)
        # self.fields['session'].queryset = Session.objects.filter(state='open').order_by('start_date')
        self.student_count = len(students)

    def get_boxes(self):
        for field_name in self.fields:
            if field_name.startswith('student_'):
                yield self[field_name]


    # def process_refund(self, user):
    #     students = []
    #     session = self.cleaned_data['session']
    #     for k, v in self.cleaned_data.items():
    #         if str(k).startswith('student_') and v:
    #             # logging.debug(k.split('_'))
    #             students.append(int(k.split('_')[1]))
    #     logging.debug(students)
    #     reg = session.registration_set.filter(student__in=students)
    #     logging.debug(reg)
    #     if len(reg) == 0:
    #         return False
    #     logging.debug(reg.values('idempotency_key', 'pay_status').annotate(ik_count=Count('idempotency_key')).order_by())
    #
    #     refund = RefundHelper()
    #     error_count = 0
    #     for ikey in reg.values('idempotency_key', 'pay_status').annotate(ik_count=Count('idempotency_key')).order_by():
    #         ireg = reg.filter(idempotency_key=ikey['idempotency_key'])
    #         cost = session.cost
    #         logging.debug(session.cost)
    #         # if ikey['pay_status'] == 'paid' and self.cleaned_data['donation']:
    #         #     square_response = {'status': 'SUCCESS'}
    #
    #         if ikey['pay_status'] == 'paid':
    #             square_response = refund.refund_with_idempotency_key(ikey['idempotency_key'],
    #                                                                  cost * 100 * ikey['ik_count'])
    #
    #         if square_response['status'] in ['PENDING', 'SUCCESS']:
    #             if user.student_set.first().student_family == reg[0].student.student_family:
    #                 EmailMessage().refund_email(user)
    #             else:
    #                 for s in reg[0].student.student_family.student_set.all():
    #                     if s.user is not None:
    #                         EmailMessage().refund_email(s.user)
    #             for r in ireg:
    #                 # if ikey['pay_status'] == 'paid' and self.cleaned_data['donation']:
    #                 #     r.pay_status = 'refund donated'
    #                 if ikey['pay_status'] in ['paid', 'refunded']:
    #                     r.pay_status = 'refunded'
    #                 else:
    #                     r.pay_status = 'canceled'
    #                 r.save()
    #         else:
    #             for r in ireg:
    #                 self.add_error(f'student_{r.student.id}', square_response['error'])
    #             error_count += 1
    #     return error_count == 0
