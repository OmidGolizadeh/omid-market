from home.models import About_the_store, Link
from products.models import Category


def show_about_site(request):
    about = About_the_store.objects.first()
    return {'about': about}


def menu_categories(request):
    top = (Category.objects.filter(related_categories__isnull=True).prefetch_related('categories__categories'))
    return {'menu_categories': top}
