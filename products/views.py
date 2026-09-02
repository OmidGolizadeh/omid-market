from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from .models import Product, Category, Category_brand, Comment, Like
from django.db.models import F
from .forms import CommentForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


class ProductView(TemplateView):
    template_name = 'products/product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.all()

        context['object_list'] = products
        context['category'] = Category.objects.all()
        context['brand'] = Category_brand.objects.all()
        context['latest_products'] = Product.objects.order_by('-created_at')[:3]

        if self.request.user.is_authenticated:
            context['liked_products'] = Like.objects.filter(user=self.request.user, product__in=products).values_list(
                'product_id', flat=True)
        else:
            context['liked_products'] = []

        return context


class ProductList(TemplateView):
    template_name = 'products/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Product.objects.all()
        context['category'] = Category.objects.all()
        context['brand'] = Category_brand.objects.all()
        context['latest_products'] = Product.objects.order_by('-created_at')[:3]
        return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Product.objects.filter(pk=obj.pk).update(view=F('view') + 1)
        obj.refresh_from_db()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_offer'] = Product.objects.exclude(pk=self.object.pk)[:5]
        context['commentForm'] = CommentForm
        if self.request.user.is_authenticated:
            context['like'] = Like.objects.filter(user=self.request.user, product=self.object).exists()
        else:
            context['like'] = False
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()
            return redirect('products:product_detail', slug=product.slug)
        context = self.get_context_data()
        context['commentForm'] = form
        return self.render_to_response(context)


@require_POST
@login_required(login_url='accounts:login')
def like_view(request, slug, pk):
    product = get_object_or_404(Product, id=pk, slug=slug)
    like = Like.objects.filter(user=request.user, product=product)
    if like.exists():
        like.delete()
        return JsonResponse({'response': 'unliked'})
    else:
        Like.objects.create(user=request.user, product=product)
        return JsonResponse({'response': 'liked'})
