from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order, PaymentInfo

class CheckoutForm(forms.ModelForm):
    """Formulario para el proceso de checkout"""
    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone', 'address', 
            'city', 'state', 'postal_code', 'payment_method', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PaymentReferenceForm(forms.ModelForm):
    """Formulario para añadir referencia de pago"""
    class Meta:
        model = PaymentInfo
        fields = ['transaction_id']
        labels = {
            'transaction_id': _('Referencia de pago')
        }
        help_texts = {
            'transaction_id': _('Ingresa el número de transferencia o referencia de tu pago')
        }