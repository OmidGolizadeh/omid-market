from django.contrib import admin
from django.utils.html import format_html
from .models import About_the_store, Contact_us, Team, Link


@admin.register(Team)
class show_Team(admin.ModelAdmin):
    list_display = ('full_name', 'expertise', 'position', 'show_image_team')

    def show_image_team(self, obj):
        if obj.image:  # بررسی وجود تصویر
            return format_html('<img src="{}" width="50px" height="50px" />', obj.image.url)
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
    list_display = ['name', 'phone', 'title']


@admin.register(Link)
class Links(admin.ModelAdmin):
    list_display = ['title', 'url']
