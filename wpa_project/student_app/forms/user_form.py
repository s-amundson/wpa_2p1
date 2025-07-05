from django.contrib.auth.models import Group
from src import MyModelForm
from django.forms.widgets import CheckboxInput, SelectDateWidget
from django.utils import timezone

from ..models import User
import logging
logger = logging.getLogger(__name__)


class UserForm(MyModelForm):

    class Meta(MyModelForm.Meta):

        model = User
        disabled_fields = ['is_member']
        hidden_fields = []
        optional_fields = ['is_board', 'is_staff', 'is_instructor', 'instructor_expire_date', 'dark_theme', 'is_active']
        required_fields = []
        fields = optional_fields + hidden_fields + disabled_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['is_board', 'is_staff', 'is_instructor', 'dark_theme', 'is_active', 'is_member']:
            self.fields[f].widget = CheckboxInput()
            self.fields[f].required = False

        self.fields['is_member'].widget.attrs.update({'disabled': 'disabled'})
        self.fields['instructor_expire_date'].widget = SelectDateWidget(
            years=range(timezone.datetime.today().year, timezone.datetime.today().year + 4, 1))
        self.fields['is_staff'].help_text = ''
        self.fields['is_active'].help_text = ''

    # def clean(self):
    #     cleaned_data = super().clean()
    #     if cleaned_data['is_instructor']:
    #         cleaned_data['is_staff'] = True

    def save(self, *args, **kwargs):
        i = super().save(*args, **kwargs)
        for g in ['instructors', 'staff', 'board']:
            i.groups.remove(Group.objects.get(name=g))
        if self.cleaned_data['is_instructor']:
            i.groups.add(Group.objects.get(name='instructors'))
            i.groups.add(Group.objects.get(name='staff'))
        if self.cleaned_data['is_staff']:
            i.groups.add(Group.objects.get(name='staff'))
        if self.cleaned_data['is_board']:
            i.groups.add(Group.objects.get(name='board'))
            i.groups.add(Group.objects.get(name='staff'))
        return i