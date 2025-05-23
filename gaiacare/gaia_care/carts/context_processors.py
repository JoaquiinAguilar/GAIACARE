from .views import get_or_create_cart

def cart_items_count(request):
    """Contexto para mostrar el número de items en el carrito en todas las páginas"""
    if request.user.is_authenticated or 'cart_id' in request.session:
        cart = get_or_create_cart(request)
        return {'cart_items_count': cart.get_total_items()}
    return {'cart_items_count': 0}