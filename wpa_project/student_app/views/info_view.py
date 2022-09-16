from django.contrib.sites.models import Site
from django.shortcuts import render
from django.views.generic.base import View
from django.http import Http404

from facebook.tasks import fetch_posts


class InfoView(View):
    def get(self, request, info):
        current_site = Site.objects.get_current()
        if info == 'about':
            return render(request, 'student_app/about.html')
        if info == 'by-laws':
            return render(request, 'student_app/by-laws.html')
        if info == 'class_description':
            return render(request, 'student_app/class_descriptions.html')
        if info == 'constitution':
            return render(request, 'student_app/constitution.html')
        if info == 'covid':
            return render(request, 'student_app/covid.html')
        if info == 'directions':
            return render(request, 'student_app/directions.html')
        if info == 'privacy':
            return render(request, 'student_app/privacy.html', {'current_site': current_site})
        if info == 'terms':
            return render(request, 'student_app/terms.html', {'current_site': current_site})
        raise Http404("Policy not found")
