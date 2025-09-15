from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'phone', 'status', 'created_at')
    search_fields = ('username', 'full_name', 'email', 'phone')
    list_filter = ('status', 'created_at')
  