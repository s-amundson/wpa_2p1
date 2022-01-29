from django.forms import ChoiceField, BooleanField
from src.model_form import MyModelForm
from ..models import PinAttendance, PinScores
from ..src import Choices

choices = Choices()


class PinAttendanceBaseForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = PinAttendance
        fields = ['bow', 'category', 'distance', 'target', 'inner_scoring', 'score', 'stars', 'event', 'student',
                  'attended', 'previous_stars']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stars'] = ChoiceField(choices=choices.stars())
        self.fields['previous_stars'] = ChoiceField(choices=choices.stars())
        self.update_attributes()
        self.fields['inner_scoring'] = BooleanField(required=False)
        self.fields['attended'] = BooleanField(required=False)


class PinAttendanceStaffForm(PinAttendanceBaseForm):

    class Meta(PinAttendanceBaseForm.Meta):
        model = PinAttendance
        hidden_fields = []
        disabled_fields = ['stars', ]
        exclude = ['event', 'student', 'category']
        optional_fields = ['bow', 'distance', 'target', 'inner_scoring', 'score', 'attended', 'previous_stars']
        fields = disabled_fields + optional_fields + hidden_fields

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)


class PinAttendanceStudentForm(PinAttendanceBaseForm):

    class Meta(PinAttendanceBaseForm.Meta):
        model = PinAttendance
        hidden_fields = []
        read_fields = ['stars', 'attended']
        exclude = ['event', 'student', 'category']
        required_fields = ['bow', 'distance', 'target', 'score', 'previous_stars']
        optional_fields = ['inner_scoring']
        fields = read_fields + optional_fields + hidden_fields + required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PinScoresForm(MyModelForm):


    class Meta(MyModelForm.Meta):
        model = PinScores
        required_fields = ['bow', 'category', 'distance', 'target', 'score', 'stars']
        fields = required_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stars'] = ChoiceField(choices=choices.stars())
        self.fields['stars'].widget.attrs.update({'class': 'form-control m-2'})
