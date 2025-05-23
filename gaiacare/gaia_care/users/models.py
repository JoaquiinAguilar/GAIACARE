from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class CustomUser(AbstractUser):
    """Modelo de usuario personalizado con campos adicionales"""
    email = models.EmailField(_('correo electrónico'), unique=True)
    phone_number = models.CharField(_('número de teléfono'), max_length=15, blank=True)
    address = models.TextField(_('dirección'), blank=True)
    city = models.CharField(_('ciudad'), max_length=100, blank=True)
    state = models.CharField(_('estado'), max_length=100, blank=True)
    postal_code = models.CharField(_('código postal'), max_length=10, blank=True)
    
    # Campos requeridos por django-allauth
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')


class UserProfile(models.Model):
    """Perfil de usuario con información adicional"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"Perfil de {self.user.email}"
    
    class Meta:
        verbose_name = _('perfil de usuario')
        verbose_name_plural = _('perfiles de usuario')


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un perfil de usuario automáticamente cuando se crea un usuario"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el perfil de usuario cuando se guarda el usuario"""
    instance.profile.save()


# Crear grupos de administradores
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_admin_groups(sender, **kwargs):
    """Crea los grupos de administradores si no existen"""
    admin_group, created = Group.objects.get_or_create(name=settings.ADMIN_GROUP)
    admin_limited_group, created = Group.objects.get_or_create(name=settings.ADMIN_LIMITED_GROUP)