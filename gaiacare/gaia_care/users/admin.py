from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile
from django.contrib.auth.models import Group
from django.conf import settings

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_groups')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Información personal'), {'fields': ('username', 'first_name', 'last_name', 'phone_number')}),
        (_('Dirección'), {'fields': ('address', 'city', 'state', 'postal_code')}),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    def get_groups(self, obj):
        """Retorna los grupos a los que pertenece el usuario como string"""
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Grupos'
    
    def get_queryset(self, request):
        """Limita los usuarios que puede ver un administrador limitado"""
        qs = super().get_queryset(request)
        
        # Superuser puede ver todo
        if request.user.is_superuser:
            return qs
        
        # Administrador normal puede ver todos excepto superusuarios
        if request.user.groups.filter(name=settings.ADMIN_GROUP).exists():
            return qs.filter(is_superuser=False)
        
        # Administrador limitado solo ve usuarios regulares
        if request.user.groups.filter(name=settings.ADMIN_LIMITED_GROUP).exists():
            return qs.filter(is_staff=False, is_superuser=False)
            
        return qs.none()
    
    def has_change_permission(self, request, obj=None):
        """Controla permisos para modificar usuarios"""
        # Si no hay objeto, está en la lista
        if not obj:
            return True
            
        # Superuser puede editar cualquier usuario
        if request.user.is_superuser:
            return True
            
        # Administrador normal puede editar todos excepto superusuarios
        if request.user.groups.filter(name=settings.ADMIN_GROUP).exists():
            if obj.is_superuser:
                return False
            return True
            
        # Administrador limitado solo puede editar usuarios regulares
        if request.user.groups.filter(name=settings.ADMIN_LIMITED_GROUP).exists():
            if obj.is_staff or obj.is_superuser:
                return False
            return True
            
        return False

admin.site.register(CustomUser, CustomUserAdmin)