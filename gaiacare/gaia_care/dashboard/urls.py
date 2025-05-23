from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='dashboard_home'),
    
    # Productos
    path('productos/', views.product_list, name='product_list'),
    path('productos/nuevo/', views.product_create, name='product_create'),
    path('productos/<int:product_id>/', views.product_detail, name='product_detail'),
    path('productos/imagen/<int:image_id>/actualizar/', views.update_product_image, name='update_product_image'),
    
    # Categorías
    path('categorias/', views.category_list, name='category_list'),
    path('categorias/<int:category_id>/', views.category_detail, name='category_detail'),
    
    # Pedidos
    path('pedidos/', views.order_list, name='order_list'),
    path('pedidos/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Usuarios
    path('usuarios/', views.user_list, name='user_list'),
    path('usuarios/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Configuración
    path('configuracion/', views.dashboard_settings, name='settings'),
]