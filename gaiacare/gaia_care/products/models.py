from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Categoría de productos"""
    name = models.CharField(_('nombre'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('descripción'), blank=True)
    image = models.ImageField(_('imagen'), upload_to='categories', blank=True, null=True)
    is_active = models.BooleanField(_('activo'), default=True)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('categoría')
        verbose_name_plural = _('categorías')
        ordering = ['name']


class Product(models.Model):
    """Modelo para los productos"""
    category = models.ForeignKey(Category, verbose_name=_('categoría'), related_name='products', on_delete=models.CASCADE)
    name = models.CharField(_('nombre'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    description = models.TextField(_('descripción'))
    price = models.DecimalField(_('precio'), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_('inventario'), default=1)
    available = models.BooleanField(_('disponible'), default=True)
    featured = models.BooleanField(_('destacado'), default=False)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('producto')
        verbose_name_plural = _('productos')
        ordering = ['-created_at']
    
    def get_main_image(self):
        """Retorna la imagen principal del producto"""
        return self.images.filter(is_main=True).first() or self.images.first()


class ProductImage(models.Model):
    """Imágenes de los productos"""
    product = models.ForeignKey(Product, verbose_name=_('producto'), related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(_('imagen'), upload_to='products')
    is_main = models.BooleanField(_('es principal'), default=False)
    alt_text = models.CharField(_('texto alternativo'), max_length=200, blank=True)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    def __str__(self):
        return f"Imagen para {self.product.name}"
    
    class Meta:
        verbose_name = _('imagen de producto')
        verbose_name_plural = _('imágenes de productos')
        ordering = ['-is_main', 'created_at']


class ProductInventory(models.Model):
    """Inventario detallado de productos"""
    product = models.OneToOneField(Product, verbose_name=_('producto'), related_name='inventory_detail', on_delete=models.CASCADE)
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    batch_number = models.CharField(_('número de lote'), max_length=100, blank=True)
    production_date = models.DateField(_('fecha de producción'), null=True, blank=True)
    expiry_date = models.DateField(_('fecha de caducidad'), null=True, blank=True)
    reorder_level = models.PositiveIntegerField(_('nivel de reorden'), default=5)
    
    def __str__(self):
        return f"Inventario de {self.product.name}"
    
    class Meta:
        verbose_name = _('inventario de producto')
        verbose_name_plural = _('inventarios de productos')


class ProductAttribute(models.Model):
    """Atributos de los productos (ej: tamaño, aroma, etc.)"""
    name = models.CharField(_('nombre'), max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('atributo de producto')
        verbose_name_plural = _('atributos de productos')


class ProductAttributeValue(models.Model):
    """Valores de los atributos para productos específicos"""
    product = models.ForeignKey(Product, verbose_name=_('producto'), related_name='attribute_values', on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, verbose_name=_('atributo'), on_delete=models.CASCADE)
    value = models.CharField(_('valor'), max_length=100)
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"
    
    class Meta:
        verbose_name = _('valor de atributo')
        verbose_name_plural = _('valores de atributos')
        unique_together = ('product', 'attribute')