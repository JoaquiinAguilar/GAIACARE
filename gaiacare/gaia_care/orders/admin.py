from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, ShippingInfo, PaymentInfo, PaymentConfig

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total',)
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = _('Total')

class ShippingInfoInline(admin.StackedInline):
    model = ShippingInfo
    can_delete = False
    
class PaymentInfoInline(admin.StackedInline):
    model = PaymentInfo
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'status', 'payment_method', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'id')
    readonly_fields = ('subtotal', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline, ShippingInfoInline, PaymentInfoInline]
    
    fieldsets = (
        (_('Información del cliente'), {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        (_('Dirección de envío'), {
            'fields': ('address', 'city', 'state', 'postal_code')
        }),
        (_('Estado y pago'), {
            'fields': ('status', 'payment_method', 'payment_reference')
        }),
        (_('Totales'), {
            'fields': ('subtotal', 'shipping_cost', 'total')
        }),
        (_('Notas y fechas'), {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo pedido
            super().save_model(request, obj, form, change)
            # Crear automáticamente los objetos relacionados
            ShippingInfo.objects.get_or_create(order=obj)
            PaymentInfo.objects.get_or_create(
                order=obj,
                defaults={'amount': obj.total}
            )
        else:
            super().save_model(request, obj, form, change)
            # Actualizar monto de pago si cambia el total
            payment, created = PaymentInfo.objects.get_or_create(
                order=obj,
                defaults={'amount': obj.total}
            )
            if not created and payment.amount != obj.total:
                payment.amount = obj.total
                payment.save()

@admin.register(PaymentConfig)
class PaymentConfigAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('bank_name', 'account_name')
    
    fieldsets = (
        (_('Información bancaria'), {
            'fields': ('bank_name', 'account_name', 'account_number', 'clabe')
        }),
        (_('Instrucciones'), {
            'fields': ('payment_instructions', 'is_active')
        }),
    )