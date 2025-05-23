from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F
from .models import Cart, CartItem
from products.models import Product
import uuid

def get_or_create_cart(request):
    """Obtiene o crea un carrito para el usuario o sesión"""
    if request.user.is_authenticated:
        # Para usuarios autenticados
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'session_id': None}
        )
    else:
        # Para usuarios anónimos
        session_id = request.session.get('cart_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['cart_id'] = session_id
        
        cart, created = Cart.objects.get_or_create(
            session_id=session_id,
            defaults={'user': None}
        )
    
    return cart

class CartView(TemplateView):
    """Vista para mostrar el carrito"""
    template_name = 'carts/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = get_or_create_cart(self.request)
        return context

class AddToCartView(View):
    """Vista para añadir productos al carrito"""
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({'error': 'Producto no especificado'}, status=400)
        
        # Obtener producto
        try:
            product = Product.objects.get(id=product_id, available=True)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Producto no disponible'}, status=404)
        
        # Verificar stock
        if product.stock < quantity:
            return JsonResponse({'error': 'Stock insuficiente'}, status=400)
        
        # Obtener o crear carrito
        cart = get_or_create_cart(request)
        
        # Añadir producto al carrito
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        # Si el producto ya estaba en el carrito, aumentar cantidad
        if not created:
            # Verificar que no se exceda el stock
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return JsonResponse({'error': 'Stock insuficiente'}, status=400)
            
            cart_item.quantity = new_quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} añadido al carrito.')
        
        # Respuesta JSON para peticiones AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'item_count': cart.get_total_items(),
                'cart_total': float(cart.get_subtotal()),
                'message': f'{product.name} añadido al carrito.'
            })
        
        # Redirección para peticiones normales
        return redirect('carts:cart')

class UpdateCartView(View):
    """Vista para actualizar la cantidad de un producto en el carrito"""
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        
        if not item_id or not action:
            return JsonResponse({'error': 'Parámetros incorrectos'}, status=400)
        
        # Obtener item del carrito
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Item no encontrado'}, status=404)
        
        # Actualizar cantidad según la acción
        if action == 'increase':
            # Verificar stock
            if cart_item.quantity >= cart_item.product.stock:
                return JsonResponse({'error': 'Stock insuficiente'}, status=400)
            
            cart_item.quantity = F('quantity') + 1
            cart_item.save()
            cart_item.refresh_from_db()
        
        elif action == 'decrease':
            if cart_item.quantity <= 1:
                cart_item.delete()
                return JsonResponse({
                    'success': True,
                    'removed': True,
                    'item_count': cart_item.cart.get_total_items(),
                    'cart_total': float(cart_item.cart.get_subtotal())
                })
            
            cart_item.quantity = F('quantity') - 1
            cart_item.save()
            cart_item.refresh_from_db()
        
        elif action == 'remove':
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'removed': True,
                'item_count': cart_item.cart.get_total_items(),
                'cart_total': float(cart_item.cart.get_subtotal())
            })
        
        # Respuesta para AJAX
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'item_total': float(cart_item.get_total()),
            'item_count': cart_item.cart.get_total_items(),
            'cart_total': float(cart_item.cart.get_subtotal())
        })

class ClearCartView(View):
    """Vista para vaciar el carrito"""
    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        cart.clear()
        
        messages.success(request, 'Carrito vaciado correctamente.')
        
        # Respuesta para AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Carrito vaciado correctamente.'
            })
        
        return redirect('carts:cart')