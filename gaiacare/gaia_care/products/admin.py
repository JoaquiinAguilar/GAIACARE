from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Category, 
    Product, 
    ProductImage, 
    ProductInventory,
    ProductAttribute,
    ProductAttributeValue
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        """Muestra una vista previa de la imagen"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "Sin imagen"
    image_preview.short_description = _('Vista previa')

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    
class ProductInventoryInline(admin.StackedInline):
    model = ProductInventory
    can_delete = False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def image_preview(self, obj):
        """Muestra una vista previa de la imagen"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "Sin imagen"
    image_preview.short_description = _('Vista previa')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        (_('Imagen'), {
            'fields': ('image', 'image_preview')
        }),
    )
    readonly_fields = ('image_preview',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available', 'featured', 'created_at', 'updated_at')
    list_filter = ('available', 'featured', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductAttributeValueInline, ProductInventoryInline]
    
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        (_('Precios e inventario'), {
            'fields': ('price', 'stock', 'available')
        }),
        (_('Opciones adicionales'), {
            'fields': ('featured',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Crear inventario si no existe
        ProductInventory.objects.get_or_create(product=obj, defaults={'sku': f'SKU-{obj.id}'})

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)