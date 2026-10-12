from django.db.models import F, Exists, OuterRef
from .models import Product, Category, Like, ProductColor

SORT_OPTIONS = {
    'newest': ('جدیدترین', ['-created_at', '-id']),
    'views': ('پربازدیدترین', ['-view', '-id']),
    'cheapest': ('ارزان‌ترین', [F('price').asc(nulls_last=True), 'id']),
}
DEFAULT_SORT = 'newest'


def get_category_tree_ids(category_ids):
    ids = set(category_ids)
    frontier = set(category_ids)
    while frontier:
        children = set(
            Category.objects.filter(related_categories__in=frontier)
            .values_list('id', flat=True)
        ) - ids
        ids |= children
        frontier = children
    return ids


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class ProductFilterMixin:
    def get_filtered_products(self):
        GET = self.request.GET
        products = Product.objects.all()

        self.selected_slugs = GET.getlist('category')
        if self.selected_slugs:
            ids = Category.objects.filter(slug__in=self.selected_slugs).values_list('id', flat=True)
            products = products.filter(Category_id__in=get_category_tree_ids(ids))

        self.min_price = to_int(GET.get('min_price'))
        self.max_price = to_int(GET.get('max_price'))
        if self.min_price is not None:
            products = products.filter(price__gte=self.min_price)
        if self.max_price is not None:
            products = products.filter(price__lte=self.max_price)

        self.only_available = GET.get('only_available') == '1'
        if self.only_available:
            in_stock = ProductColor.objects.filter(product=OuterRef('pk'), number__gt=0)
            products = products.filter(Exists(in_stock))

        self.only_warranty = GET.get('only_warranty') == '1'
        if self.only_warranty:
            has_warranty = Product.warranty.through.objects.filter(product_id=OuterRef('pk'))
            products = products.filter(Exists(has_warranty))
        self.sort = GET.get('sort')
        if self.sort not in SORT_OPTIONS:
            self.sort = DEFAULT_SORT
        products = products.order_by(*SORT_OPTIONS[self.sort][1])
        return products

    def get_filter_context(self, products):
        user = self.request.user
        query = self.request.GET.copy()
        query.pop('sort', None)
        query.pop('page', None)
        return {
            'object_list': products,
            'latest_products': Product.objects.order_by('-created_at')[:3],
            'selected_slugs': self.selected_slugs,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'only_available': self.only_available,
            'only_warranty': self.only_warranty,
            'liked_products': (
                Like.objects.filter(user=user, product__in=products).values_list('product_id', flat=True)
                if user.is_authenticated else []
            ),
            'sort_options': [(key, label) for key, (label, _) in SORT_OPTIONS.items()],
            'current_sort': self.sort,
            'base_query': query.urlencode(),
        }
