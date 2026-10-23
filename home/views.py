from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from .models import Team, About_the_store
from .forms import Contact_Form
from products.models import Product, Category, Like
from django.db.models import Count


class Home(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_products = Product.objects.select_related('Category', 'brand').annotate(
            comment_count=Count('comment')
        )
        products = Product.objects.all()
        context['product'] = base_products.order_by('-created_at')[:8]
        context['category'] = Category.objects.all()
        context['most_viewed_view'] = base_products.order_by('-view')[:8]
        context['discounted_products'] = base_products.filter(discount_percent__gt=0)[:8]
        context['mobile_products'] = base_products.filter(Category__title='گوشی موبایل')[:8]
        context['laptop_products'] = base_products.filter(Category__title='لپ تاپ و الترابوک')[:8]
        context['computer_products'] = base_products.filter(Category__title='تجهیزات کامپیوتر')[:8]
        context['camera_products'] = base_products.filter(Category__title='دوربین')[:8]

        if self.request.user.is_authenticated:
            context['liked_products'] = set(
                Like.objects.filter(user=self.request.user, product__in=products).values_list(
                    'product_id', flat=True)
            )

        else:
            context['liked_products'] = set()

        return context


class About(TemplateView):
    template_name = 'home/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Team.objects.all()
        context['about'] = About_the_store.objects.first()
        return context


class Contact(FormView):
    template_name = 'home/contact.html'
    form_class = Contact_Form
    success_url = reverse_lazy('home:contact')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = About_the_store.objects.all()
        return context


class Fag(TemplateView):
    template_name = 'home/faq.html'
