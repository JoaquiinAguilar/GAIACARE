from django.urls import path
from . import admin_views

urlpatterns = [
    path('productimage/<int:image_id>/make-main/', admin_views.make_main_image, name='make_main_image'),
    path('reorder-images/', admin_views.reorder_images, name='reorder_images'),
    path('get-attributes/<int:category_id>/', admin_views.get_attributes_for_category, name='get_attributes_for_category'),
]