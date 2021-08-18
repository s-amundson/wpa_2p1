from django.forms import ModelForm

from ..models import CostsModel


class CostsForm(ModelForm):

    class Meta:
        model = CostsModel
        exclude = []
