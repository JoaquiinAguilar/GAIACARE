from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from products.models import Product, Category

class HomeView(TemplateView):
    """Vista para la página principal"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener productos destacados
        context['featured_products'] = Product.objects.filter(featured=True, available=True)[:3]
        # Obtener categorías activas
        context['categories'] = Category.objects.filter(is_active=True)[:4]
        return context

class AboutView(TemplateView):
    """Vista para la página Sobre Nosotros"""
    template_name = 'core/about.html'

class ContactView(TemplateView):
    """Vista para la página de Contacto"""
    template_name = 'core/contact.html'