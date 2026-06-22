from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Team , About_the_store


class Home(TemplateView):
    template_name = 'home/index.html'


class About(TemplateView):
    template_name = 'home/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Team.objects.all()
        context['about'] = About_the_store.objects.first()
        return context
