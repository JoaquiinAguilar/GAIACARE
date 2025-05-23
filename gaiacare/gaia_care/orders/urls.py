from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('completado/<int:order_id>/', views.OrderCompleteView.as_view(), name='order_complete'),
    path('pago/<int:order_id>/', views.PaymentReferenceView.as_view(), name='payment_reference'),
    path('mis-pedidos/', views.OrderListView.as_view(), name='order_list'),
    path('detalle/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
]