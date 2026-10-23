from django.contrib import admin
from .models import Product, Category, Category_brand, ProductColor, Product_Image, Warranty, Comment, Like, Rating
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea, TextInput


class Rating_show(admin.TabularInline):
    model = Rating
    extra = 1
    fields = ['user', 'product', 'comment', 'score', 'created_at']
    readonly_fields = ('user', 'product', 'comment', 'score', 'created_at',)
    ordering = ('created_at',)


@admin.register(Rating)
class Rating_show_score(admin.ModelAdmin):
    list_display = ['user', 'product', 'comment', 'score', 'created_at']
    list_filter = ['product', 'score']
    search_fields = ['user', 'product', 'score']
    readonly_fields = ('user', 'product', 'comment', 'score', 'created_at',)
    ordering = ('created_at',)


class Product_Image_show(admin.TabularInline):
    model = Product_Image
    extra = 1
    fields = ('images', 'show_image_product', 'created_at')
    readonly_fields = ('show_image_product', 'created_at')
    ordering = ['created_at']

    def show_image_product(self, obj):
        if obj.pk and obj.images:
            return format_html(
                '<img src="{}" width="90" height="90" style="object-fit:cover; border-radius:8px;" />',
                obj.images.url
            )
        return "بدون تصویر"

    show_image_product.short_description = "پیش‌نمایش"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'body_short', 'created_at']
    list_filter = ['created_at', 'product']  # فیلتر تاریخ و محصول
    search_fields = ['body', 'user__username', 'user__full_name', 'product__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    list_per_page = 20

    def body_short(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body

    body_short.short_description = 'متن کامنت'


class Comment_show(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('user', 'body', 'parent', 'parent_display', 'created_at')
    readonly_fields = ('user', 'parent_display', 'created_at')
    ordering = ['-created_at']

    def parent_display(self, obj):
        if not obj.parent:
            return format_html('<span style="color:#999;">بدون منبع</span>')

        parent = obj.parent
        text = parent.body[:70] + '...' if len(parent.body) > 70 else parent.body

        return format_html(
            '''
            <div style="background:#f1f5f9; padding:7px 11px; border-radius:6px; border-right:3px solid #3b82f6; max-width:340px;">
                <div style="font-size:12px; color:#64748b; margin-bottom:4px;">
                    <strong>{}</strong> • {}
                </div>
                <div style="font-size:13px; color:#1e293b; line-height:1.4;">{}</div>
            </div>
            ''',
            parent.user,
            parent.created_at.strftime('%Y/%m/%d %H:%M') if parent.created_at else '',
            text
        )

    parent_display.short_description = 'پیش‌نمایش منبع'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            if request.resolver_match.kwargs.get('object_id'):
                product_id = request.resolver_match.kwargs.get('object_id')
                kwargs["queryset"] = Comment.objects.filter(product_id=product_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class CommentFormSet(formset):
            def save_new(self, form, commit=True):
                # کاربر رو به صورت خودکار روی ادمین فعلی تنظیم می‌کنه
                instance = form.save(commit=False)
                instance.user = request.user
                if commit:
                    instance.save()
                return instance

        return CommentFormSet

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'rows': 3,
                'style': 'width:100%; min-height:70px; resize:vertical;'
            })
        },
    }


class Like_show(admin.TabularInline):
    model = Like
    extra = 0
    fields = ('user', 'created_at')
    readonly_fields = ('user', 'created_at')
    ordering = ['-created_at']
    can_delete = False


@admin.register(Product)
class Product_show(admin.ModelAdmin):
    list_display = (
        'title', 'short_description_truncated', 'price', 'show_image_product', 'get_total_stock', 'view', 'sales_count',
        'likes_count', 'comments_count')
    readonly_fields = ('created_at',)
    search_fields = ['title', 'short_description_truncated', ]
    ordering = ['title', '-created_at']
    list_filter = ['created_at']
    inlines = (Product_Image_show, Like_show, Rating_show, Comment_show)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Comment) and not instance.user_id:
                instance.user = request.user
            instance.save()
        formset.save_m2m()

    def short_description_truncated(self, obj):
        text = obj.short_description
        if text and len(text) > 50:
            return text[:50] + '...'
        return text

    def show_image_product(self, obj):
        if obj.images:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:50%;" />', obj.images.url)
        return "بدون تصویر"

    def get_total_stock(self, obj):
        return obj.total_stock

    def likes_count(self, obj):
        count = obj.likes.count()
        if count > 0:
            return format_html(
                '<span style="background:#FFC107; color:white; padding:3px 8px; border-radius:12px; font-size:12px;">❤️ {}</span>',
                count
            )
        return format_html('<span style="color:#94a3b8;">۰ لایک</span>')

    def comments_count(self, obj):
        count = obj.comment.count()
        if count > 0:
            return format_html(
                '<span style="background:#3b82f6; color:white; padding:3px 8px; border-radius:12px; font-size:12px;">💬 {}</span>',
                count
            )
        return format_html('<span style="color:#94a3b8;">۰ کامنت</span>')

    show_image_product.short_description = "تصویر"
    short_description_truncated.short_description = 'توضیحات (خلاصه)'
    get_total_stock.short_description = 'تعداد کل'
    likes_count.short_description = 'لایک ها'
    comments_count.short_description = 'کامت ها'


@admin.register(Category)
class Category_show(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created_at']
    readonly_fields = ('created_at',)
    search_fields = ('title', 'slug')
    ordering = ['title', 'created_at']
    filter_horizontal = ('categories',)


@admin.register(Category_brand)
class Category_brand_show(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('created_at',)
    ordering = ['title', 'created_at']


@admin.register(ProductColor)
class ProductColor_show(admin.ModelAdmin):
    list_display = ['product', 'name_color', 'show_color', 'number']
    readonly_fields = ('created_at',)
    ordering = ['product', 'created_at']

    def show_color(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: #{}; border-radius: 50%; border: 1px solid #ccc;"></div>',
                obj.color_code
            )
        return "بدون رنگ"

    show_color.short_description = 'نمایش رنگ'


@admin.register(Warranty)
class Warranty_show(admin.ModelAdmin):
    list_display = ['title']
