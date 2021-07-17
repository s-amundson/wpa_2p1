from django.contrib.sites.models import Site
from django.shortcuts import render
from django.views.generic.base import View


class TermsView(View):
    def get(self, request):
        current_site = Site.objects.get_current()
        return render(request, 'student_app/terms.html', {'current_site': current_site})
