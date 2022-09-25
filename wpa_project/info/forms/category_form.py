from src.model_form import MyModelForm
from ..models import Category


class CategoryForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Category
        required_fields = ['title']
        optional_fields = []
        fields = optional_fields + required_fields
