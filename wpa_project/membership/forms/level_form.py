from src.model_form import MyModelForm
from ..models import Level


class LevelForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Level
        required_fields = ['cost']
        optional_fields = ['min_age', 'max_age', 'is_family', 'additional_cost']
        fields = optional_fields + required_fields
