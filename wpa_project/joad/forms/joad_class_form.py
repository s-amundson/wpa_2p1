from django.forms import ModelForm, DateTimeField
from src.model_form import MyModelForm
from ..models import JoadClass


class ClassForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = JoadClass
        required_fields = ['class_date']
        disabled_fields = ['session']
        fields = required_fields + disabled_fields

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['class_date'] = DateTimeField()
        self.fields['class_date'].widget.attrs.update({'class': 'form-control m-2'})