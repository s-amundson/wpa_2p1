from src.model_form import MyModelForm
from ..models import Policy, PolicyText, ACCESS
from django.forms import ModelForm, CharField, CheckboxInput, ChoiceField

class PolicyForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Policy
        required_fields = ['title', 'access']
        optional_fields = []
        fields = optional_fields + required_fields


class PolicyTextForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = PolicyText
        required_fields = ['status', 'policy']
        optional_fields = ['title', 'is_html']
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['title_text'] = CharField(label='Title')
        self.fields['title_text'].widget.attrs.update({'class': 'form-control m-2'})
        self.fields['title_access'] = ChoiceField(label='Access', choices=ACCESS)
        self.fields['is_html'].widget = CheckboxInput()
        self.fields['is_html'].required = False
        if self.instance.id:
            self.fields['policy'].widget.attrs.update({'class': 'form-control m-2', 'readonly': 'readonly'})