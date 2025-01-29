
from django.contrib import admin
from .models import UserAccount
# Register your models here.

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_admin', 'is_superuser', 'is_active']