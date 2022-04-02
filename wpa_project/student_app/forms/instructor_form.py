from django.forms import ModelForm
from django.conf import settings
from django.apps import apps


class InstructorForm(ModelForm):

    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ('instructor_expire_date', 'instructor_level')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor_expire_date'].widget.attrs.update({'placeholder': 'YYYY-MM-DD'})
        self.fields['instructor_expire_date'].error_messages = {'required': '*', 'invalid': "Enter a valid date in YYYY-MM-DD format"}
        self.fields['instructor_level'].widget.attrs.update({'placeholder': 'Level'})
