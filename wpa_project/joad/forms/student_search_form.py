from django.forms import TextInput, CheckboxInput
from django import forms

from student_app.forms import SearchColumnsForm


class SearchColumnsForm(SearchColumnsForm):
    last_event = forms.BooleanField(required=False, label='Show pin records from last event')
