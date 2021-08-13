from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import BeginnerClass, CostsModel, Student, StudentFamily, User


class UserAdmin(UserAdmin):

    model = User
    list_display = ['email', 'username', 'is_board', 'is_instructor']


admin.site.register(BeginnerClass)
admin.site.register(CostsModel)
admin.site.register(Student)
admin.site.register(StudentFamily)
admin.site.register(User, UserAdmin)
