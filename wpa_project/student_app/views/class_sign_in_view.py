import logging
import base64
from binascii import a2b_base64
from django.core.files.base import ContentFile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import  HttpResponseForbidden
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from ..forms import ClassSignInForm
from ..models import BeginnerClass, ClassRegistration
from ..src import ClassRegistrationHelper
logger = logging.getLogger(__name__)


class ClassSignInView(LoginRequiredMixin, View):
    def get(self, request, reg_id):
        cr = get_object_or_404(ClassRegistration, pk=reg_id)
        form = ClassSignInForm()
        return render(request, 'student_app/class_sign_in.html', {'form': form, 'student': cr.student})

    def post(self, request, reg_id):
        logging.debug(request.POST)
        cr = get_object_or_404(ClassRegistration, pk=reg_id)
        logging.debug(cr)
        form = ClassSignInForm(request.POST)
        if form.is_valid():
            logging.debug('valid')
            logging.debug(form.cleaned_data)
            image_b64 = form.cleaned_data['signature']
            img_format, imgstr = image_b64.split(';base64,')
            ext = img_format.split('/')[-1]
            cr.signature = ContentFile(base64.b64decode(imgstr), name=f'{reg_id}.{ext}')
            cr.attended = True
            cr.save()

        return render(request, 'student_app/message.html', {'message': ' Thank You'})



