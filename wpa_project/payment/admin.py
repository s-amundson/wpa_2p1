from django.contrib import admin

from .models import CostsModel


@admin.register(CostsModel)
class CostModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'enabled']