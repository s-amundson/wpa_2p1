from django.forms import BooleanField, CheckboxInput

from src.model_form import MyModelForm
from ..models import Category


class CategoryForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Category
        required_fields = ['title', 'email', 'is_public']
        optional_fields = []
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_public'] = BooleanField(
            widget=CheckboxInput(attrs={'class': "m-2"}),
            required=False,
            initial=False)