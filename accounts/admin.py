from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from accounts.models import User, Otp, Address, Province, City
from accounts.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
import pprint
import jdatetime

UserModel = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ['show_image_user', 'username', 'full_name', 'email', 'is_admin']
    list_filter = ['is_admin', 'created_at']
    readonly_fields = ('created_at',)
    fieldsets = (
        ('کاربر', {
            'fields': ('username', 'email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('full_name', 'image', 'date_of_birth',)}),
        ('اطلاعات تماس', {'fields': ('phone_number', 'landline',)}),
        ('اطلاعات هویتی', {'fields': ('national_code', 'card_number', 'created_at')}),
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


@admin.register(Otp)
class Otp_show(admin.ModelAdmin):
    list_display = ['username', 'email', 'code', 'token', 'expiration_date_show']
    list_filter = ['expiration_date']

    def expiration_date_show(self, obj):
        return obj.expiration_date.strftime(f"تاریخ %Y/%m/%d | ساعت %H:%M")

    expiration_date_show.short_description = 'تاریخ'


@admin.register(Address)
class Address_show(admin.ModelAdmin):
    list_display = ['user', 'postal_code', 'receiver_delivery', 'created_at']
    ordering = ['user', 'created_at']
    list_filter = ['created_at']


class City_show(admin.TabularInline):
    model = City
    extra = 1
    fields = ['name', 'province', ]
    list_filter = ['province']
    ordering = ['province']


@admin.register(Province)
class Province_show(admin.ModelAdmin):
    list_display = ['name']
    inlines = (City_show,)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    # اضافه شدن نام کاربری و آی‌پی به لیست اصلی
    list_display = ('session_key', 'get_username', 'get_ip', 'expire_date')

    # اضافه شدن نام کاربری و آی‌پی به صفحه جزئیات (Detail View)
    readonly_fields = ('get_username', 'get_ip', 'session_data_decoded')
    search_fields = ('session_key',)
    date_hierarchy = 'expire_date'

    def get_username(self, obj):
        """ استخراج آیدی کاربر از نشست و پیدا کردن نام او (Time Complexity: O(1)) """
        session_data = obj.get_decoded()
        uid = session_data.get('_auth_user_id')
        if uid:
            try:
                return UserModel.objects.get(pk=uid).username
            except UserModel.DoesNotExist:
                return "کاربر حذف شده"
        return "کاربر مهمان (Guest)"

    get_username.short_description = 'نام کاربری'

    def get_ip(self, obj):
        """ استخراج آی‌پی ذخیره شده در نشست """
        session_data = obj.get_decoded()
        return session_data.get('ip_address', 'نامشخص')

    get_ip.short_description = 'آی‌پی (IP)'

    def session_data_decoded(self, obj):
        return pprint.pformat(obj.get_decoded())

    session_data_decoded.short_description = 'محتوای کامل نشست'

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'action_flag', 'object_repr')
    list_filter = ('action_flag', 'content_type')
    search_fields = ('user__username', 'object_repr')
    date_hierarchy = 'action_time'
    list_select_related = ('user', 'content_type')

    # امنیت: ادمین‌های دیگر نباید بتوانند تاریخچه کارهای انجام شده را دستکاری یا حذف کنند
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(Group)
# admin.site.register(Province)
