import logging
from django.forms import IntegerField
from django.forms.models import BaseModelFormSet
from ..models import Minutes, Report
from src.model_form import MyModelForm
logger = logging.getLogger(__name__)


class ReportForm(MyModelForm):
    report_index = 0
    report_id = IntegerField(required=False)

    class Meta(MyModelForm.Meta):
        model = Report
        optional_fields = ['report']
        hidden_fields = ['minutes', 'owner', 'report_id']
        fields = optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        self.report_index = kwargs.get('report_index', 0)
        if 'report_index' in kwargs:
            kwargs.pop('report_index')
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['report_id'].initial = self.instance.id
        self.auto_id = 'report_%s' + f'_{self.report_index}'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2 minutes-input'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2 minutes-input', 'style': 'display:none'})
        self.fields['report'].widget.attrs.update({'cols': 80, 'rows': 3,
                                                   'class': 'form-control m-2 report minutes-input'})
        if not edit:
            self.fields['report'].widget.attrs.update({'disabled': 'disabled'})


class ReportForm2(MyModelForm):
    template_name_div = "minutes/forms/report_form2.html"

    class Meta(MyModelForm.Meta):
        model = Report
        optional_fields = ['report']
        hidden_fields = ['minutes', 'owner']
        fields = optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['report'].widget.attrs.update({'cols': 80, 'rows': 3,
                                                   'class': 'form-control m-2 report minutes-input'})


class ReportFormset(BaseModelFormSet):
    template_name_div = 'minutes/forms/report_formset.html'
