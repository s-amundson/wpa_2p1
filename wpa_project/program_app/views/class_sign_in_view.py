from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from student_app.forms import WaiverForm

from ..models import ClassRegistration

import logging
logger = logging.getLogger(__name__)


class ClassSignInView(LoginRequiredMixin, View):
    def get(self, request, reg_id):
        cr = get_object_or_404(ClassRegistration, pk=reg_id)
        form = WaiverForm(cr.student, age_date=cr.beginner_class.class_date)
        logging.debug(bool(cr.student.signature))
        logging.debug(cr.student.signature is not None)
        return render(request, 'program_app/class_sign_in.html',
                      {'form': form, 'student': cr.student, 'Img': cr.student.signature,
                       'is_signed': bool(cr.student.signature)})

    def post(self, request, reg_id):
        logging.debug(request.POST)
        cr = get_object_or_404(ClassRegistration, pk=reg_id)
        sf = cr.student.student_family
        form = WaiverForm(cr.student, request.POST)
        if form.is_valid():
            logging.debug('valid')
            logging.debug(form.cleaned_data)
            if form.make_pdf(cr.beginner_class.class_date):

                cr.attended = True
                cr.save()

                form.send_pdf()

                return HttpResponseRedirect(reverse('programs:beginner_class',
                                                    kwargs={'beginner_class': cr.beginner_class.id}))

        logging.debug(form.errors)
        return render(request, 'program_app/class_sign_in.html',
                      {'form': form, 'student': cr.student, 'Img': cr.student.signature,
                       'is_signed': bool(cr.student.signature), 'message': 'invalid signature'})
