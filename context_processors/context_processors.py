from home.models import About_the_store, Link


def show_about_site(request):
    about = About_the_store.objects.first()
    return {'about': about}
