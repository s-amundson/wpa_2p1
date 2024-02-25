from django import forms
from django.utils import timezone


class MemberExpireDateForm(forms.Form):
    query_date = forms.DateField(
        widget=forms.SelectDateWidget(years=range(timezone.datetime.today().year, timezone.datetime.today().year + 3, 1)),
        required=False)
    csv_export = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check"}), required=False)
    order_by = forms.ChoiceField(choices=[('last', 'Last Name'), ('first', 'First Name'), ('expire', 'Expire Date')])
