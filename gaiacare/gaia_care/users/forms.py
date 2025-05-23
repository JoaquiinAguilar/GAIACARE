from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    """Formulario para crear un nuevo usuario"""
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')

class CustomUserChangeForm(UserChangeForm):
    """Formulario para modificar un usuario en el admin"""
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number',
                 'address', 'city', 'state', 'postal_code', 'is_active')

class UserUpdateForm(forms.ModelForm):
    """Formulario para actualizar información del usuario"""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'postal_code')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class ProfileUpdateForm(forms.ModelForm):
    """Formulario para actualizar el perfil del usuario"""
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }