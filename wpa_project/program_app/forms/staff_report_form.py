from django import forms
from django.utils import timezone


import logging

logger = logging.getLogger(__name__)


class StaffReportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'] = forms.DateField(initial=timezone.datetime(year=2022, month=1, day=1),
                                                    widget=forms.SelectDateWidget(
                                                        years=range(timezone.datetime.today().year, 2022, -1)))
        self.fields['end_date'] = forms.DateField(initial=timezone.now().date(),
                                                  widget=forms.SelectDateWidget(
                                                      years=range(timezone.datetime.today().year, 2022, -1)))

