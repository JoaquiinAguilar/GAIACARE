from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from products.models import Product

class Order(models.Model):
    """Modelo para los pedidos"""
    STATUS_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('pagado', _('Pagado')),
        ('enviado', _('Enviado')),
        ('entregado', _('Entregado')),
        ('cancelado', _('Cancelado')),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('transferencia', _('Transferencia Bancaria')),
        ('deposito', _('Depósito Bancario')),
        ('efectivo', _('Pago en Efectivo')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('usuario'), on_delete=models.CASCADE)
    full_name = models.CharField(_('nombre completo'), max_length=100)
    email = models.EmailField(_('correo electrónico'))
    phone = models.CharField(_('teléfono'), max_length=15)
    address = models.TextField(_('dirección'))
    city = models.CharField(_('ciudad'), max_length=100)
    state = models.CharField(_('estado'), max_length=100)
    postal_code = models.CharField(_('código postal'), max_length=10)
    status = models.CharField(_('estado'), max_length=20, choices=STATUS_CHOICES, default='pendiente')
    payment_method = models.CharField(_('método de pago'), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='transferencia')
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(_('costo de envío'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    payment_reference = models.CharField(_('referencia de pago'), max_length=100, blank=True)
    notes = models.TextField(_('notas'), blank=True)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.user.email}"
    
    def update_total(self):
        """Actualiza el total del pedido"""
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.total = self.subtotal + self.shipping_cost
        self.save()
    
    class Meta:
        verbose_name = _('pedido')
        verbose_name_plural = _('pedidos')
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Elementos individuales en un pedido"""
    order = models.ForeignKey(Order, verbose_name=_('pedido'), related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_('producto'), on_delete=models.CASCADE)
    price = models.DecimalField(_('precio'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('cantidad'), default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total(self):
        """Calcula el total del item"""
        return self.price * self.quantity
    
    class Meta:
        verbose_name = _('elemento de pedido')
        verbose_name_plural = _('elementos de pedido')


class ShippingInfo(models.Model):
    """Información de envío para pedidos"""
    STATUS_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('procesando', _('Procesando')),
        ('enviado', _('Enviado')),
        ('entregado', _('Entregado')),
        ('devuelto', _('Devuelto')),
    )
    
    order = models.OneToOneField(Order, verbose_name=_('pedido'), related_name='shipping', on_delete=models.CASCADE)
    tracking_number = models.CharField(_('número de seguimiento'), max_length=100, blank=True)
    carrier = models.CharField(_('transportista'), max_length=100, blank=True)
    status = models.CharField(_('estado'), max_length=20, choices=STATUS_CHOICES, default='pendiente')
    shipped_date = models.DateTimeField(_('fecha de envío'), null=True, blank=True)
    delivered_date = models.DateTimeField(_('fecha de entrega'), null=True, blank=True)
    notes = models.TextField(_('notas'), blank=True)
    
    def __str__(self):
        return f"Envío para Pedido #{self.order.id}"
    
    class Meta:
        verbose_name = _('información de envío')
        verbose_name_plural = _('información de envíos')

class PaymentInfo(models.Model):
    """Información de pago para pedidos"""
    STATUS_CHOICES = (
        ('pendiente', _('Pendiente')),
        ('procesando', _('Procesando')),
        ('completado', _('Completado')),
        ('fallido', _('Fallido')),
        ('reembolsado', _('Reembolsado')),
    )
    
    order = models.OneToOneField(Order, verbose_name=_('pedido'), related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(_('monto'), max_digits=10, decimal_places=2)
    status = models.CharField(_('estado'), max_length=20, choices=STATUS_CHOICES, default='pendiente')
    transaction_id = models.CharField(_('ID de transacción'), max_length=100, blank=True)
    payment_date = models.DateTimeField(_('fecha de pago'), null=True, blank=True)
    notes = models.TextField(_('notas'), blank=True)
    
    def __str__(self):
        return f"Pago para Pedido #{self.order.id}"
    
    class Meta:
        verbose_name = _('información de pago')
        verbose_name_plural = _('información de pagos')


class PaymentConfig(models.Model):
    """Configuración para los datos de pago"""
    bank_name = models.CharField(_('nombre del banco'), max_length=100)
    account_name = models.CharField(_('nombre del beneficiario'), max_length=100)
    account_number = models.CharField(_('número de cuenta'), max_length=20)
    clabe = models.CharField(_('CLABE'), max_length=20)
    payment_instructions = models.TextField(_('instrucciones adicionales'), blank=True)
    is_active = models.BooleanField(_('activo'), default=True)
    
    def __str__(self):
        return f"Configuración de pago: {self.bank_name}"
    
    class Meta:
        verbose_name = _('configuración de pago')
        verbose_name_plural = _('configuraciones de pago')

class PaymentConfig(models.Model):
    """Configuración para los datos de pago"""
    bank_name = models.CharField(_('nombre del banco'), max_length=100)
    account_name = models.CharField(_('nombre del beneficiario'), max_length=100)
    account_number = models.CharField(_('número de cuenta'), max_length=20)
    clabe = models.CharField(_('CLABE'), max_length=20)
    payment_instructions = models.TextField(_('instrucciones adicionales'), blank=True)
    is_active = models.BooleanField(_('activo'), default=True)
    
    def __str__(self):
        return f"Configuración de pago: {self.bank_name}"
    
    class Meta:
        verbose_name = _('configuración de pago')
        verbose_name_plural = _('configuraciones de pago')