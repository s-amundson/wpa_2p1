from django.contrib import admin

from .models import Member, Membership


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'join_date', 'begin_date', 'expire_date', 'level']


# @admin.register(Membership)
# class MemberShipAdmin(admin.ModelAdmin):
#     list_display = ['id', 'students', 'effective_date', 'level', 'pay_status', 'idempotency_key']
