import logging
from django.forms import BooleanField, IntegerField
from django.utils import timezone

from src import MyModelForm
from ..models import Business, BusinessUpdate

logger = logging.getLogger(__name__)


class BusinessForm(MyModelForm):
    business_id = IntegerField(required=False)
    # report_number = IntegerField(required=False)
    resolved_bool = BooleanField(required=False, initial=False)

    class Meta(MyModelForm.Meta):
        model = Business
        read_fields = []
        hidden_fields = ['business_id', 'minutes']
        optional_fields = ['business', 'resolved', 'resolved_bool']
        fields = optional_fields + hidden_fields + read_fields

    def __init__(self, *args, **kwargs):
        old_business = kwargs.get('old', False)
        self.report_index = kwargs.get('report', 0)
        if 'old' in kwargs:
            kwargs.pop('old')
        if 'report' in kwargs:
            kwargs.pop('report')
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['business_id'].initial = self.instance.id
        # self.fields['report_number'].inital = self.report_index
        self.auto_id = 'business_%s' + f'_{self.report_index}'
        self.fields['business'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})
        if old_business: # if true; disable the input so it can't be modified
            self.fields['business'].widget.attrs.update({'class': 'form-control m-2', 'readonly': 'readonly'})
        if self.initial.get('resolved', None) is not None:
            self.fields['resolved_bool'].initial = True

        else:
            self.fields['resolved_bool'].initial = False
        self.fields['resolved_bool'].widget.attrs.update({'class': "form-check-input resolved-check"})


class BusinessUpdateForm(MyModelForm):
    report_index = 0
    update_id = IntegerField(required=False)

    class Meta(MyModelForm.Meta):
        model = BusinessUpdate
        read_fields = []
        hidden_fields = ['business', 'update_id']
        optional_fields = ['update_text', ]
        fields = optional_fields + hidden_fields + read_fields

    def __init__(self, *args, **kwargs):
        old_update = kwargs.get('old', False)
        self.report_index = kwargs.get('report', 0)
        if 'old' in kwargs:
            kwargs.pop('old')
        if 'report' in kwargs:
            kwargs.pop('report')
        super().__init__(*args, **kwargs)
        self.update_date = None
        if self.instance:
            self.fields['update_id'].initial = self.instance.id
            self.update_date = self.instance.update_date
        if self.update_date is None:
            self.update_date = timezone.now()
        self.auto_id = 'update_%s' + f'_{self.report_index}'
        self.fields['update_text'].widget.attrs.update({'cols': 60, 'rows': 3, 'class': 'form-control m-2 update'})
        if old_update:
            self.fields['update_text'].widget.attrs.update({'readonly': 'readonly'})
