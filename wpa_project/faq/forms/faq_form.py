from src.model_form import MyModelForm
from ..models import Faq


class FaqForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Faq
        required_fields = ['category', 'question', 'answer', 'status']
        optional_fields = []
        fields = optional_fields + required_fields
