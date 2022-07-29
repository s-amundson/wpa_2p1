from django import forms
from django.utils.datetime_safe import date


class MemberExpireDateForm(forms.Form):
    query_date = forms.DateField(
        widget=forms.SelectDateWidget(years=range(date.today().year, date.today().year + 3, 1)),
        required=False)
    csv_export = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check"}), required=False)
