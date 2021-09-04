from django.forms import ModelForm

from ..models import Level


class LevelForm(ModelForm):

    class Meta:
        model = Level
        exclude = []
        optional_fields = ['min_age', 'max_age', 'is_family', 'additional_cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.Meta.optional_fields:
            self.fields[f].required = False
