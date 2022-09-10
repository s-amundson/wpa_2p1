from django.forms import Form, ModelChoiceField, RadioSelect
from src.model_form import MyModelForm
from ..models import Category, Faq


class FaqForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Faq
        required_fields = ['category', 'question', 'answer', 'status']
        optional_fields = []
        fields = optional_fields + required_fields


class FaqFilterForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'] = ModelChoiceField(Category.objects.all(), empty_label="---------", required=False)

