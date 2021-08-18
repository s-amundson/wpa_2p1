from django.forms import ModelForm

from ..models import BeginnerClass


class BeginnerClassForm(ModelForm):

    class Meta:
        model = BeginnerClass
        exclude = []
