from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('categorias/', views.CategoryListView.as_view(), name='category_list'),
    path('categoria/<slug:category_slug>/', views.ProductListView.as_view(), name='category_products'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]