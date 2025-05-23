from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/products/', include('products.admin_urls')),  # URLs personalizadas para admin
    path('accounts/', include('allauth.urls')),
    path('productos/', include('products.urls')),
    path('pedidos/', include('orders.urls')),
    path('usuarios/', include('users.urls')),
    path('carrito/', include('carts.urls')),
    path('panel/', include('dashboard.urls')),  # Panel de control frontend
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)