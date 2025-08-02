from src.model_form import MyModelForm
from ..models import Policy, PolicyText, ACCESS
from django.forms import CharField, CheckboxInput, ChoiceField, HiddenInput
from django_ckeditor_5.widgets import CKEditor5Widget


class PolicyForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Policy
        required_fields = ['title', 'access']
        optional_fields = []
        fields = optional_fields + required_fields


class PolicyTextForm(MyModelForm):
    class Meta(MyModelForm.Meta):
        model = PolicyText
        required_fields = ['status', 'policy', 'user']
        optional_fields = ['title']
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        self.fields['title_text'] = CharField(label='Title')
        self.fields['title_text'].widget.attrs.update({'class': 'form-control m-2'})
        self.fields['title_access'] = ChoiceField(label='Access', choices=ACCESS)
        self.fields['policy'].widget = CKEditor5Widget(
            attrs={"class": "django_ckeditor_5"}, config_name="no-color"
        )
        if self.instance.id:
            self.fields['policy'].widget.attrs.update({'class': 'form-control m-2', 'readonly': 'readonly'})
        self.fields['user'].widget = HiddenInput()