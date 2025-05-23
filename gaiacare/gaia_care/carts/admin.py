from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_total',)
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = _('Total')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'get_items_count', 'get_cart_total', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'session_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_items_count(self, obj):
        return obj.get_total_items()
    get_items_count.short_description = _('Cantidad de items')
    
    def get_cart_total(self, obj):
        return obj.get_subtotal()
    get_cart_total.short_description = _('Total')