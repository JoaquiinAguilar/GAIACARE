from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('agregar/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('actualizar/', views.UpdateCartView.as_view(), name='update_cart'),
    path('vaciar/', views.ClearCartView.as_view(), name='clear_cart'),
]