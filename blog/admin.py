from django.contrib import admin
from blog import models
from django.utils.html import format_html


@admin.register(models.Category)
class CategoryLabelShow(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created_at']
    list_filter = ['created_at']


@admin.register(models.Label_Article)
class CategoryLabelShow(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created_at']
    list_filter = ['created_at']


@admin.register(models.Article)
class ArticleShow(admin.ModelAdmin):
    list_display = ['title', 'author', 'show_image', 'views', 'updated_at', 'created_at']
    list_filter = ['created_at', 'updated_at']
    ordering = ['created_at']
    search_fields = ['title', 'category__title', 'author__full_name', 'author__username']

    @admin.display(description='تصویر')
    def show_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="90" height="90" '
                'style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return 'بدون تصویر'


@admin.register(models.Comment)
class CommentShow(admin.ModelAdmin):
    list_display = ['article', 'id', 'user', 'body_short', 'parent', 'created_at']
    list_filter = ['created_at', 'article']
    search_fields = ['body', 'user__username', 'user__full_name', 'article__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    list_select_related = ['article', 'user', 'parent']
    autocomplete_fields = ['article']  # نیاز به search_fields در ProductAdmin دارد
    list_per_page = 20

    @admin.display(description='متن کامنت')
    def body_short(self, obj):
        body = obj.body or ''
        return body[:50] + '...' if len(body) > 50 else body

    def get_readonly_fields(self, request, obj=None):
        # user فقط روی کامنت‌های موجود readonly باشد
        if obj:
            return ['user', 'created_at']
        return ['created_at']

    def get_exclude(self, request, obj=None):
        # هنگام افزودن، user خودکار پر می‌شود و در فرم نمایش داده نمی‌شود
        return None if obj else ['user']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            object_id = request.resolver_match.kwargs.get('object_id')

            if object_id:
                comment = models.Comment.objects.filter(pk=object_id).first()

                if comment:
                    kwargs['queryset'] = models.Comment.objects.filter(
                        article_id=comment.article_id
                    ).exclude(pk=comment.pk)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
