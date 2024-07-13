import logging
from django.forms import BooleanField
from django.forms.models import BaseModelFormSet
from django.utils import timezone

from src import MyModelForm
from ..models import Business, BusinessUpdate

logger = logging.getLogger(__name__)


class BusinessForm(MyModelForm):
    resolved_bool = BooleanField(required=False, initial=False)

    class Meta(MyModelForm.Meta):
        model = Business
        read_fields = []
        hidden_fields = ['minutes']
        optional_fields = ['business', 'resolved', 'resolved_bool']
        fields = optional_fields + hidden_fields + read_fields

    def __init__(self, *args, **kwargs):
        self.action_url = kwargs.pop('action_url')

        super().__init__(*args, **kwargs)
        logger.warning(self.initial)
        self.fields['business'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2'})
        self.fields['resolved_bool'].initial = False
        self.fields['resolved_bool'].widget.attrs.update({'class': "form-check-input resolved-check"})
        if self.instance.id:
            # self.fields['business_id'].initial = self.instance.id
            if self.instance.minutes and self.instance.minutes.end_time is not None:
                self.fields['business'].widget.attrs.update({'readonly': 'readonly'})
                self.fields['resolved_bool'].widget.attrs.update({'disabled': 'disabled'})
            if self.instance.resolved is not None:
                self.fields['resolved_bool'].initial = True
                self.fields['business'].widget.attrs.update({'readonly': 'readonly'})
            self.auto_id = 'business_%s' + f'_{self.instance.id}'


        for f in self.Meta.fields:
            self.fields[f].widget.attrs['class'] += ' business-input'


class BusinessFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.minutes = None
        if 'minutes' in kwargs:
            self.minutes = kwargs.pop('minutes')
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['minutes'] = self.minutes
        return kwargs

class BusinessUpdateForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = BusinessUpdate
        read_fields = []
        hidden_fields = ['business', 'update_date']
        optional_fields = ['update_text', ]
        fields = optional_fields + hidden_fields + read_fields

    def __init__(self, *args, **kwargs):
        minutes = None
        if 'minutes' in kwargs:
            minutes = kwargs.pop('minutes')
        super().__init__(*args, **kwargs)
        self.fields['update_text'].widget.attrs.update({'cols': 60, 'rows': 3, 'class': 'form-control m-2 update'})
        logger.warning(minutes)
        if minutes is None or minutes.end_time is not None:
            self.fields['update_text'].widget.attrs.update({'readonly': 'readonly'})
        if self.instance.id:
            if self.instance.update_date + timezone.timedelta(hours=12) < timezone.now() or self.instance.business.resolved is not None:
                logger.warning('read only')
                self.fields['update_text'].widget.attrs.update({'readonly': 'readonly'})
