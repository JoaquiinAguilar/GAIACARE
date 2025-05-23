from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse

from .models import Order, OrderItem, ShippingInfo, PaymentInfo, PaymentConfig
from .forms import CheckoutForm, PaymentReferenceForm
from carts.views import get_or_create_cart
from products.models import Product
import decimal

class CheckoutView(LoginRequiredMixin, View):
    """Vista para el proceso de checkout"""
    template_name = 'orders/checkout.html'
    
    def get(self, request, *args, **kwargs):
        # Verificar si hay items en el carrito
        cart = get_or_create_cart(request)
        if cart.items.count() == 0:
            messages.warning(request, 'Tu carrito está vacío.')
            return redirect('carts:cart')
        
        # Pre-llenar formulario con datos del usuario
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
            'email': request.user.email,
            'phone': request.user.phone_number,
            'address': request.user.address,
            'city': request.user.city,
            'state': request.user.state,
            'postal_code': request.user.postal_code,
        }
        form = CheckoutForm(initial=initial_data)
        
        # Calcular costos de envío (ejemplo: $100 fijos)
        shipping_cost = decimal.Decimal('100.00')
        subtotal = cart.get_subtotal()
        total = subtotal + shipping_cost
        
        context = {
            'form': form,
            'cart': cart,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'total': total,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        if cart.items.count() == 0:
            messages.warning(request, 'Tu carrito está vacío.')
            return redirect('carts:cart')
        
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Calcular totales
            shipping_cost = decimal.Decimal('100.00')
            subtotal = cart.get_subtotal()
            total = subtotal + shipping_cost
            
            with transaction.atomic():
                # Crear orden
                order = form.save(commit=False)
                order.user = request.user
                order.subtotal = subtotal
                order.shipping_cost = shipping_cost
                order.total = total
                order.save()
                
                # Crear items de la orden
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        price=cart_item.product.price,
                        quantity=cart_item.quantity
                    )
                    
                    # Actualizar inventario
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()
                
                # Crear info de envío y pago
                ShippingInfo.objects.create(order=order)
                PaymentInfo.objects.create(
                    order=order,
                    amount=total,
                    status='pendiente'
                )
                
                # Vaciar carrito
                cart.clear()
                
                messages.success(request, f'¡Pedido #{order.id} creado correctamente!')
                return redirect('orders:order_complete', order_id=order.id)
        
        # Si el formulario no es válido
        context = {
            'form': form,
            'cart': cart,
            'subtotal': cart.get_subtotal(),
            'shipping_cost': decimal.Decimal('100.00'),
            'total': cart.get_subtotal() + decimal.Decimal('100.00'),
        }
        return render(request, self.template_name, context)

class OrderCompleteView(LoginRequiredMixin, DetailView):
    """Vista para mostrar confirmación de pedido"""
    model = Order
    template_name = 'orders/order_complete.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get(self, request, *args, **kwargs):
        # Verificar que el pedido pertenezca al usuario
        order = self.get_object()
        if order.user != request.user:
            messages.error(request, 'No tienes permiso para ver este pedido.')
            return redirect('orders:order_list')
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_form'] = PaymentReferenceForm()
        
        # Obtener la configuración de pago activa de la base de datos
        try:
            payment_config = PaymentConfig.objects.filter(is_active=True).first()
            if payment_config:
                context['bank_details'] = {
                    'bank_name': payment_config.bank_name,
                    'account_name': payment_config.account_name,
                    'account_number': payment_config.account_number,
                    'clabe': payment_config.clabe,
                }
                context['payment_instructions'] = payment_config.payment_instructions
            else:
                # Usar valores por defecto si no hay configuración
                context['bank_details'] = {
                    'bank_name': 'Tu Banco',
                    'account_name': 'Tu Nombre o Empresa',
                    'account_number': '0123456789',
                    'clabe': '012345678901234567',
                }
        except:
            # En caso de error, usar valores por defecto
            context['bank_details'] = {
                'bank_name': 'Tu Banco',
                'account_name': 'Tu Nombre o Empresa',
                'account_number': '0123456789',
                'clabe': '012345678901234567',
            }
        
        return context
    
class OrderListView(LoginRequiredMixin, ListView):
    """Vista para listar pedidos del usuario"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class PaymentReferenceView(LoginRequiredMixin, View):
    """Vista para añadir referencia de pago"""
    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        form = PaymentReferenceForm(request.POST, instance=order.payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.status = 'procesando'
            payment.payment_date = timezone.now()
            payment.save()
            
            # Actualizar estado del pedido
            order.status = 'pagado'
            order.payment_reference = payment.transaction_id
            order.save()
            
            messages.success(request, 'Referencia de pago enviada correctamente. Confirmaremos tu pago pronto.')
            return redirect('orders:order_detail', order_id=order.id)
        
        messages.error(request, 'Por favor verifica la información.')
        return redirect('orders:order_complete', order_id=order.id)

class OrderDetailView(LoginRequiredMixin, DetailView):
    """Vista para mostrar detalles de un pedido"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get(self, request, *args, **kwargs):
        # Verificar que el pedido pertenezca al usuario
        order = self.get_object()
        if order.user != request.user:
            messages.error(request, 'No tienes permiso para ver este pedido.')
            return redirect('orders:order_list')
        
        return super().get(request, *args, **kwargs)