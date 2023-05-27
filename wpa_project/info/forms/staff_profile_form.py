from src.model_form import MyModelForm
from ..models import StaffProfile


class StaffProfileForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = StaffProfile
        required_fields = ['student', 'bio', 'status']
        optional_fields = ['image']
        fields = optional_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(user__is_staff=True)
        self.multipart = True
