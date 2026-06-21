from django.contrib import admin

from .models import About_the_store, Contact_us, Team, Link


@admin.register(Team)
class show_Team(admin.ModelAdmin):
    list_display = ('full_name', 'expertise', 'position')


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
