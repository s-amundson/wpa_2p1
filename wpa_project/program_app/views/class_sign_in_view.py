from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils import timezone

from student_app.views import WaiverView
from ..models import ClassRegistration
from payment.src import RefundHelper
import logging
logger = logging.getLogger(__name__)


class ClassSignInView(WaiverView):
    class_registration = None

    def test_func(self):
        rid = self.kwargs.get('reg_id', None)
        # logging.debug(rid)
        if rid is not None:
            self.class_registration = get_object_or_404(ClassRegistration, pk=rid)
            self.class_date = self.class_registration.beginner_class.class_date.date()
            self.student = self.class_registration.student
            self.success_url = reverse_lazy('programs:class_attend_list',
                                            kwargs={'beginner_class': self.class_registration.beginner_class.id})
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False

    def update_attendance(self):
        self.class_registration.attended = True
        self.class_registration.save()
        # Cancel future beginner classes by this student
        cr = ClassRegistration.objects.filter(
            beginner_class__class_date__gt=timezone.now().replace(hour=23, minute=59, second=59),
            student=self.student)
        waiting = cr.filter(pay_status='waiting')
        waiting.update(pay_status='canceled')
        for r in cr.filter(pay_status='paid'):
            if not r == self.class_registration:
                refund = RefundHelper().refund_with_idempotency_key(r.idempotency_key, r.beginner_class.cost * 100)
                if refund['status'] == 'SUCCESS':
                    r.pay_status = 'refunded'
                    r.save()
