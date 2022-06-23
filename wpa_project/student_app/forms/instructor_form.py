from django.forms import ModelForm, SelectDateWidget
from django.conf import settings
from django.apps import apps
from django.utils.datetime_safe import date


class InstructorForm(ModelForm):

    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ('instructor_expire_date', 'instructor_level')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor_expire_date'].widget = SelectDateWidget(
            years=range(date.today().year, date.today().year + 3, 1))
        self.fields['instructor_level'].widget.attrs.update({'placeholder': 'Level'})
