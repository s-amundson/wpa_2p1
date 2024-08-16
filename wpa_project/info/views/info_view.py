from django.contrib.sites.models import Site
from django.shortcuts import render
from django.views.generic.base import View
from django.http import Http404


class InfoView(View):
    def get(self, request, info):
        current_site = Site.objects.get_current()
        if info == 'about':
            return render(request, 'info/about.html')
        if info == 'by-laws':
            return render(request, 'info/by-laws.html')
        if info == 'class_description':
            return render(request, 'info/class_descriptions.html')
        if info == 'constitution':
            return render(request, 'info/constitution.html')
        if info == 'covid':
            return render(request, 'info/covid.html')
        if info == 'directions':
            return render(request, 'info/directions.html')
        if info == 'privacy':
            return render(request, 'info/privacy.html', {'current_site': current_site})
        if info == 'rules':
            return render(request, 'info/rules.html')
        if info == 'terms':
            return render(request, 'info/terms.html', {'current_site': current_site})
        raise Http404("Policy not found")
