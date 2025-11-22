from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category
import django_filters

class ProductFilter(django_filters.FilterSet):
    """Filtros para productos"""
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nombre')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Precio mínimo')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Precio máximo')
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'min_price', 'max_price']

class ProductListView(ListView):
    """Vista para listar productos"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        
        # Filtrar por categoría si se especifica
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Aplicar búsqueda si existe
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Aplicar filtros
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['filter'] = self.filterset
        
        # Obtener categoría actual si existe
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
        
        return context

class ProductDetailView(DetailView):
    """Vista para detalles de un producto"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Productos relacionados (misma categoría)
        context['related_products'] = Product.objects.filter(
            category=product.category,
            available=True
        ).exclude(id=product.id)[:3]
        
        return context

class CategoryListView(ListView):
    """Vista para listar categorías"""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)

def search_suggestions(request):
    """Vista para sugerencias de búsqueda (autocomplete)"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        available=True
    ).values('name', 'slug', 'price')[:5]
    
    results = list(products)
    return JsonResponse(results, safe=False)