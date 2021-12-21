import logging
from ..models import Decision
from src.model_form import MyModelForm
logger = logging.getLogger(__name__)


class DecisionForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Decision
        optional_fields = ['decision_date']  # , 'minutes']
        required_fields = ['text']
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        edit = kwargs.get('edit', False)
        if 'edit' in kwargs:
            kwargs.pop('edit')
        super().__init__(*args, **kwargs)
        self.auto_id = 'decision_%s'
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['text'].widget.attrs.update({'cols': 80, 'rows': 3, 'class': 'form-control m-2 decision'})
        # if not edit:
        #     self.fields['report'].widget.attrs.update({'disabled': 'disabled'})
