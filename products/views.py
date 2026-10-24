from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, View
from .models import Product, Category, Category_brand, Comment, Like, ProductColor, Rating
from django.db.models import F, Exists, OuterRef, Q
from .forms import CommentForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .mixins import ProductFilterMixin, to_int
from django.contrib import messages


class ProductView(ProductFilterMixin, TemplateView):
    template_name = 'products/product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_filtered_products()
        context.update(self.get_filter_context(products))
        context['brand'] = Category_brand.objects.all()
        return context


class ProductList(ProductFilterMixin, TemplateView):
    template_name = 'products/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_filtered_products()
        context.update(self.get_filter_context(products))
        context['brand'] = Category_brand.objects.all()
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
            context['user_rating'] = Rating.objects.filter(
                product=self.object, user=self.request.user
            ).first()
            context['like'] = Like.objects.filter(user=self.request.user, product=self.object).exists()
        else:
            context['user_rating'] = None
            context['like'] = False
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        self.object = self.get_object()
        product = self.object
        body = (request.POST.get('body') or '').strip()
        score = to_int(request.POST.get('score'))
        if not body and score is None:
            messages.error(request, 'لطفاً امتیاز یا دیدگاه خود را وارد کنید.')
            return redirect('products:product_detail', slug=product.slug)

        comment = None
        if body:
            form = CommentForm(request.POST)
            if not form.is_valid():
                context = self.get_context_data()
                context['commentForm'] = form
                return self.render_to_response(context)
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()

        if score is not None and 1 <= score <= 5:
            rating, created = Rating.objects.get_or_create(user=request.user, product=product,
                                                           defaults={'score': score, 'comment': comment})
            if not created:
                rating.score = score
                if comment:
                    rating.comment = comment
                rating.save()
            product.update_score()

        return redirect('products:product_detail', slug=product.slug)


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


class Search_view(View):
    def get(self, request):
        q = request.GET.get('q')

        if q:
            products = Product.objects.filter(
                Q(title__icontains=q) |
                Q(short_description__icontains=q) |
                Q(description__icontains=q) |
                Q(brand__title__icontains=q) |
                Q(Category__title__icontains=q)
            ).distinct()
        else:
            products = Product.objects.none()

        return render(request, 'products/product.html', {
            'object_list': products,
            'q': q,
        })
