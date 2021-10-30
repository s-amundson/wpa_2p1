from django.forms import ModelForm


class MyModelForm(ModelForm):

    class Meta:
        disabled_fields = []
        hidden_fields = []
        optional_fields = []
        required_fields = []
        read_fields = []
        fields = optional_fields + hidden_fields + disabled_fields + required_fields + read_fields
        #
        # def __init__(self, *args, **kwargs):
        #     # model = None
        #     self.fields = self.optional_fields + self.hidden_fields + self.disabled_fields + self.required_fields


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.Meta.disabled_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'disabled': 'disabled'})
        for f in self.Meta.hidden_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'style': 'display:none'})
        for f in self.Meta.optional_fields:
            self.fields[f].required = False
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
        for f in self.Meta.read_fields:
            self.fields[f].widget.attrs.update({'class': 'form-control m-2', 'readonly': 'readonly'})
        for f in self.Meta.required_fields:
            self.fields[f].widget.attrs.update({'class': 'form-control m-2'})
