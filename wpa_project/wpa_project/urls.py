"""wpa_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from student_app.views import SignupView

urlpatterns = [
    path('', include('student_app.urls', namespace='registration')),
    path('accounts/signup/', SignupView.as_view(), name="account_signup"),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('contact_us/', include('contact_us.urls', namespace='contact_us')),
    path('events/', include('event.urls', namespace='events')),
    path('facebook/', include('facebook.urls', namespace='facebook')),
    path('information/', include('info.urls', namespace='information')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('joad/', include('joad.urls', namespace='joad')),
    path('membership/', include('membership.urls', namespace='membership')),
    path('minutes/', include('minutes.urls', namespace='minutes')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('programs/', include('program_app.urls', namespace='programs')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
