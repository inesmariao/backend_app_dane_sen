from django.contrib import admin
from users.models import CustomUser

# CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_staff', 'created_at')
    ordering = ('-created_at',)

