from django.contrib import admin
from .models import Faq


class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'content',)


admin.site.register(Faq, FaqAdmin)
