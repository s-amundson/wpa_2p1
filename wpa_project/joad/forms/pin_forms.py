from django.forms import ChoiceField, BooleanField, CheckboxInput
from django.forms import model_to_dict
from src.model_form import MyModelForm
from ..models import PinAttendance, PinScores
from ..src import Choices
import logging
logger = logging.getLogger(__name__)
choices = Choices()


class PinAttendanceBaseForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = PinAttendance
        fields = ['bow', 'category', 'distance', 'target', 'inner_scoring', 'score', 'stars', 'event', 'student',
                  'attended', 'previous_stars', 'award_received', 'pay_method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(self.instance)
        self.fields['stars'] = ChoiceField(choices=choices.stars())
        self.fields['previous_stars'] = ChoiceField(choices=choices.stars())
        self.update_attributes()
        self.fields['inner_scoring'] = BooleanField(required=False)
        self.fields['attended'] = BooleanField(required=False)
        self.fields['award_received'] = BooleanField(required=False)
        self.fields['award_received'].label = 'Student has received their award.'
        self.fields['award_received'].widget.attrs.update({'class': 'm-2', 'disabled': 'disabled'})
        self.instruction = ''
        self.pay_amount = 0

    def calculate_pins(self):
        """Calculates the pins based off of target size, distance, bow class and score"""
        self.instance.stars = 0
        logger.debug(self.instance.score)
        logger.debug(model_to_dict(self.instance))
        rows = PinScores.objects.filter(category=self.instance.category,
                                        bow=self.instance.bow,
                                        distance=self.instance.distance,
                                        target=self.instance.target,
                                        inner_scoring=self.instance.inner_scoring,
                                        score__lte=self.instance.score)
        logger.debug(len(rows))
        for row in rows:
            if row.stars > self.instance.stars:
                self.instance.stars = row.stars
        logger.debug(self.instance.stars)
        return self.instance.stars - self.instance.previous_stars


class PinAttendanceStaffForm(PinAttendanceBaseForm):

    class Meta(PinAttendanceBaseForm.Meta):
        model = PinAttendance
        hidden_fields = []
        disabled_fields = ['stars', ]
        exclude = ['event', 'student', 'category']
        optional_fields = ['bow', 'distance', 'target', 'inner_scoring', 'score', 'attended', 'previous_stars',
                           'award_received', 'pay_method']
        fields = disabled_fields + optional_fields + hidden_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logger.debug('here')
        self.instruction = 'Staff responsibility is to mark the student as attending. ' \
                           'All other fields are optional and the responsibility of the student/guardian.'
        self.fields['pay_method'].required = False

        if self.instance and self.instance.pay_status in ['paid', 'cash']:
            self.instruction = 'Please verify that the information filled out is correct'
            for f in self.Meta.optional_fields:
                self.fields[f].required = False
                if type(self.fields[f]) == BooleanField:
                    self.fields[f].widget.attrs.update({'class': 'm-2', 'disabled': 'disabled'})
                else:
                    self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'readonly': 'readonly'})
            if self.instance.pay_status == 'cash' and self.instance.stars:
                # self.fields['pay_method'].initial = 'cash'
                self.pay_amount = self.instance.stars * self.instance.event.pin_cost

            self.fields['payment_received'] = BooleanField(initial=self.instance.pay_status == 'paid', required=False)
            if self.instance.pay_status == 'paid':
                self.fields['award_received'].widget.attrs.pop('disabled')
            logger.debug(self.fields['award_received'].widget.attrs)


class PinAttendanceStudentForm(PinAttendanceBaseForm):

    class Meta(PinAttendanceBaseForm.Meta):
        model = PinAttendance
        disabled_fields = ['award_received']
        read_fields = ['stars', 'attended']
        exclude = ['event', 'student', 'category']
        required_fields = ['bow', 'distance', 'target', 'score', 'previous_stars', 'pay_method']
        optional_fields = ['inner_scoring']
        fields = read_fields + optional_fields + disabled_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attended'].widget.attrs.update({'class': 'm-2', 'readonly': 'readonly'})
        self.instruction = 'Please fill out all fields below or verify that the information filled out is correct'
        logger.warning(self.instance.pay_status)
        if self.instance and self.instance.pay_status == 'cash':
            self.fields['pay_method'].initial = 'cash'



class PinScoresForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = PinScores
        required_fields = ['bow', 'category', 'distance', 'target', 'score', 'stars']
        optional_fields = ['inner_scoring']
        fields = required_fields + optional_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stars'] = ChoiceField(choices=choices.stars())
        self.fields['stars'].widget.attrs.update({'class': 'form-control m-2'})
        self.fields['inner_scoring'] = BooleanField(widget=CheckboxInput(
            attrs={'class': "m-2 student-check"}), required=False, initial=True)
