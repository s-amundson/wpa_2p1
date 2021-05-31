from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
import logging


from ..forms import ClassRegistrationForm
from ..models import StudentFamily, BeginnerClass

logger = logging.getLogger(__name__)


class ClassRegistrationView(LoginRequiredMixin, View):
    def get(self, request):
        classes = BeginnerClass.get_open_classes()
        students = StudentFamily.objects.filter(user=request.user)[0].student_set.all()
        form = ClassRegistrationForm()

        return render(request, 'student_app/index.html', {'form': form, 'students': students, 'classes': classes})

    def post(self, request):
        pass

    #     beginner_class = models.ForeignKey(BeginnerClass, on_delete=models.SET_NULL, null=True)
    #     student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    #     new_student = models.BooleanField()
    #     pay_status = models.CharField(max_length=20)
    #     idempotency_key = models.UUIDField(default=str(uuid.uuid4()))
    #     reg_time = models.DateField()