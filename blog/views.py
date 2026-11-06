from django.db.models import F, Model
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView,ListView
from blog.models import Category, Article, Comment
from products.models import Product
from .forms import CommentForm


class BlogView(ListView):
    model = Article
    template_name = 'blog/blog.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        return Article.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_viewed_products'] = Product.objects.all().order_by('-view')[:4]
        context['most_viewed_blog'] = Article.objects.all().order_by('-views')[:4]
        return context


class BlogDetailView(DetailView):
    model = Article
    template_name = 'blog/blog_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Article.objects.filter(pk=obj.pk).update(views=F('views') + 1)
        obj.refresh_from_db()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_viewed_products'] = Product.objects.all().order_by('-view')[:4]
        context['most_viewed_blog'] = Article.objects.all().order_by('-views')[:4]
        context['comments_form'] = CommentForm
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        self.object = self.get_object()
        article = self.object
        body = (request.POST.get('body') or '').strip()
        comment = None
        if body:
            form = CommentForm(request.POST)
            if not form.is_valid():
                context = self.get_context_data()
                context['comments_form'] = form
                return self.render_to_response(context)
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
        return redirect('blog:blog_detail', slug=article.slug)
