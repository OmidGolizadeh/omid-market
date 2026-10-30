from home.models import About_the_store, BannerLink, Link
from products.models import Category


def show_about_site(request):
    about = About_the_store.objects.first()
    return {'about': about}


def menu_categories(request):
    top = (Category.objects.filter(related_categories__isnull=True).prefetch_related('categories__categories'))
    return {'menu_categories': top}


def footer_links(request):
    links = BannerLink.objects.filter(second_url=True).order_by('order', 'id')
    links_about = Link.objects.all().exclude(title='')
    return {'footer_links': links, 'footer_links_about': links_about}
