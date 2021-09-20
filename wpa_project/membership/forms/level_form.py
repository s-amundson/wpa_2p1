from django.forms import ModelForm
from src.model_form import MyModelForm
from ..models import Level


class LevelForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Level
        optional_fields = ['min_age', 'max_age', 'is_family', 'additional_cost']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     for f in self.Meta.optional_fields:
    #         self.fields[f].required = False
