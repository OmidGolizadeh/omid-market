from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from accounts.models import User
from accounts.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ['show_image_user', 'username', 'full_name', 'email', 'is_admin']
    list_filter = ['is_admin']
    fieldsets = (
        ('کاربر', {
            'fields': ('username', 'email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('full_name', 'image', 'date_of_birth',)}),
        ('اطلاعات تماس', {'fields': ('phone_number', 'landline',)}),
        ('اطلاعات هویتی', {'fields': ('national_code', 'card_number',)}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),)
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'password1', 'password2',), }),
        ('اطلاعات شخصی', {'fields': ('full_name', 'phone_number', 'image', 'date_of_birth',), }),)

    search_fields = ['username', 'email', 'full_name']
    ordering = ['username']
    filter_horizontal = []

    def show_image_user(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:50%;" />', obj.image.url)
        return "بدون تصویر"

    show_image_user.short_description = "تصویر"



admin.site.unregister(Group)
