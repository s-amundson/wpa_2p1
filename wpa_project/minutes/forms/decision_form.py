import logging
from django.forms import IntegerField
from ..models import Decision
from src.model_form import MyModelForm
logger = logging.getLogger(__name__)


class DecisionForm(MyModelForm):
    decision_id = IntegerField(required=False)

    class Meta(MyModelForm.Meta):
        model = Decision
        hidden_fields = ['decision_id']
        optional_fields = ['decision_date']  # , 'minutes']
        required_fields = ['text']
        fields = hidden_fields + optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        self.report_index = kwargs.get('report_index', 0)
        if 'report_index' in kwargs:
            kwargs.pop('report_index')
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['decision_id'].initial = self.instance.id
        self.auto_id = f'decision_%s_{self.report_index}'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['text'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 decision'})
        # if not edit:
        #     self.fields['report'].widget.attrs.update({'disabled': 'disabled'})
