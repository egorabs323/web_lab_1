from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_birth', 'profile_photo')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('date_birth',)

    @admin.display(description='Фотография')
    def profile_photo(self, obj):
        if obj.photo:
            return mark_safe(f"<img src='{obj.photo.url}' width='70' style='border-radius: 4px;'>")
        return 'Нет фото'
