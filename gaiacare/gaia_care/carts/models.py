from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from products.models import Product

class Cart(models.Model):
    """Modelo para el carrito de compras"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('usuario'), on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(_('ID de sesión'), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    def __str__(self):
        return f"Carrito {'de ' + self.user.email if self.user else 'anónimo'}"
    
    def get_total_items(self):
        """Retorna el número total de items en el carrito"""
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """Calcula el subtotal del carrito"""
        return sum(item.get_total() for item in self.items.all())
    
    def clear(self):
        """Elimina todos los items del carrito"""
        self.items.all().delete()
    
    class Meta:
        verbose_name = _('carrito')
        verbose_name_plural = _('carritos')
        ordering = ['-created_at']


class CartItem(models.Model):
    """Elementos individuales en el carrito"""
    cart = models.ForeignKey(Cart, verbose_name=_('carrito'), related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_('producto'), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('cantidad'), default=1)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total(self):
        """Calcula el total del item"""
        return self.product.price * self.quantity
    
    class Meta:
        verbose_name = _('elemento de carrito')
        verbose_name_plural = _('elementos de carrito')
        unique_together = ('cart', 'product')