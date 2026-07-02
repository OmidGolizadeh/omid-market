from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from .models import Team, About_the_store
from .forms import Contact_Form


class Home(TemplateView):
    template_name = 'home/index.html'


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
