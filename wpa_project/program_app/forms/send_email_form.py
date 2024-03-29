from django import forms

from student_app.forms import SendEmailForm
from ..src import EmailMessage
from student_app.models import User, Student


class SendClassEmailForm(SendEmailForm):
    def __init__(self, *args, **kwargs):
        self.beginner_class = kwargs.pop('beginner_class')
        super().__init__(*args, **kwargs)
        self.fields.pop('recipients')
        self.fields['attending_only'] = forms.BooleanField(widget=forms.CheckboxInput(
                attrs={'class': "m-2 student-check"}), required=False)

    def send_message(self):
        em = EmailMessage()
        users = User.objects.filter(is_active=True)
        class_registrations = self.beginner_class.event.registration_set.filter(pay_status__in=['paid', 'admin'])
        if self.cleaned_data['attending_only']:
            class_registrations = class_registrations.filter(attended=True)
        student_list = []
        for cr in class_registrations:
            student_list.append(cr.student.id)
        students = Student.objects.filter(id__in=student_list)
        # students = students.exclude(user__in=User.objects.filter(is_staff=True, is_active=True))
        em.bcc_from_students(students)
        if len(em.bcc) > 0:
            em.send_message(self.cleaned_data['subject'], self.cleaned_data['message'])
