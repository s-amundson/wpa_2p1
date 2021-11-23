from django.contrib.sites.models import Site
from django.shortcuts import render
from django.views.generic.base import View
from django.http import Http404


class PolicyView(View):
    def get(self, request, policy):
        current_site = Site.objects.get_current()
        if policy == 'covid':
            return render(request, 'student_app/covid_policy.html')
        if policy == 'privacy':
            return render(request, 'student_app/privacy.html', {'current_site': current_site})
        raise Http404("Policy not found")
