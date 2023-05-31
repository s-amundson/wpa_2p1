from src.model_form import MyModelForm
from ..models import Announcement


class AnnouncementForm(MyModelForm):

    class Meta(MyModelForm.Meta):
        model = Announcement
        required_fields = ['begin_date', 'end_date', 'announcement', 'status']
        optional_fields = []
        fields = optional_fields + required_fields
