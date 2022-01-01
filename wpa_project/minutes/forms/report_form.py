import logging
from django.forms import ModelForm
from ..models import Report
from src.model_form import MyModelForm
logger = logging.getLogger(__name__)


class ReportForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Report
        optional_fields = ['report']
        hidden_fields = ['minutes', 'owner']
        fields = optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        super().__init__(*args, **kwargs)
        self.auto_id = 'report_%s'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['report'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 report'})
        if not edit:
            self.fields['report'].widget.attrs.update({'disabled': 'disabled'})
