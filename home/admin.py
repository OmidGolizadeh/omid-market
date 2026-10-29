from django.contrib import admin
from django.utils.html import format_html
from .models import About_the_store, Contact_us, Team, Link, BannerLink
from .forms import BannerLinkForm
import jdatetime


@admin.register(BannerLink)
class BannerLinkAdmin(admin.ModelAdmin):
    form = BannerLinkForm
    list_display = ('image_thumb', 'title', 'url', 'main_banner', 'second_banner', 'second_url', 'order')
    list_display_links = ('image_thumb', 'title')
    list_editable = ('order',)
    readonly_fields = ('image_preview',)
    list_filter = ('order', 'main_banner', 'second_banner', 'second_url','created_at')
    fields = (
        'title', 'image', 'image_preview', 'url',
        'main_banner', 'second_banner', 'second_url', 'order',
    )

    @admin.display(description='تصویر')
    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px; width:auto; border-radius:4px;">',
                obj.image.url,
            )
        return '—'

    @admin.display(description='پیش‌نمایش بنر')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:500px; max-height:300px; border-radius:6px;">',
                obj.image.url,
            )
        return 'هنوز تصویری آپلود نشده است'


@admin.register(Team)
class show_Team(admin.ModelAdmin):
    list_display = ('full_name', 'expertise', 'position', 'show_image_team')

    def show_image_team(self, obj):
        if obj.image:  # بررسی وجود تصویر
            return format_html('<img src="{}" width="100px" height="50px" />', obj.image.url)
        return "بدون تصویر"  # یا می‌توانید یک جایگزین نمایش دهید

    show_image_team.short_description = "تصویر"  # عنوان ستونتصویر'


@admin.register(About_the_store)
class About_site(admin.ModelAdmin):
    list_display = ['short_description_truncated', 'phone']

    def short_description_truncated(self, obj):
        text = obj.short_description
        if text and len(text) > 50:
            return text[:50] + '...'
        return text

    short_description_truncated.short_description = 'توضیحات (خلاصه)'


@admin.register(Contact_us)
class Contact(admin.ModelAdmin):
    list_display = ['name', 'phone', 'title', 'created_at_show']
    list_filter = ['created_at']

    def created_at_show(self, obj):
        return obj.created_at.strftime(f"تاریخ %Y/%m/%d | ساعت %H:%M")

    created_at_show.short_description = 'تاریخ'


@admin.register(Link)
class Links(admin.ModelAdmin):
    list_display = ['title', 'url']
