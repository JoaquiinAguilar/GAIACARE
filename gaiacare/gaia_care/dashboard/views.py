from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from datetime import timedelta

from products.models import Product, Category, ProductImage
from orders.models import Order, OrderItem
from users.models import CustomUser

# Verificar si el usuario es administrador
def is_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_staff or user.is_superuser or user.groups.filter(name__in=['Administradores', 'Administradores Limitados']).exists()

@login_required
@user_passes_test(is_admin)
def dashboard_home(request):
    """Vista principal del panel de control"""
    # Obtener estadísticas generales
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_users = CustomUser.objects.filter(is_staff=False, is_superuser=False).count()
    
    # Pedidos
    total_orders = Order.objects.count()
    total_sales = Order.objects.filter(status__in=['pagado', 'enviado', 'entregado']).aggregate(Sum('total'))['total__sum'] or 0
    
    # Pedidos recientes
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Productos más vendidos
    top_products = OrderItem.objects.values('product__name', 'product__id').annotate(
        units_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-units_sold')[:5]
    
    # Ventas por día (últimos 7 días)
    last_week = timezone.now() - timedelta(days=7)
    sales_by_day = Order.objects.filter(
        created_at__gte=last_week,
        status__in=['pagado', 'enviado', 'entregado']
    ).values('created_at__date').annotate(
        total_sales=Sum('total')
    ).order_by('created_at__date')
    
    # Preparar datos para el gráfico
    chart_labels = []
    chart_data = []
    for day in sales_by_day:
        chart_labels.append(day['created_at__date'].strftime('%d/%m'))
        chart_data.append(float(day['total_sales']))
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_users': total_users,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'section': 'home'
    }
    
    return render(request, 'dashboard/dashboard_home.html', context)

@login_required
@user_passes_test(is_admin)
def product_list(request):
    """Lista de productos para administración"""
    products = Product.objects.all().order_by('-created_at')
    
    # Filtros
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    status = request.GET.get('status')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if status:
        if status == 'available':
            products = products.filter(available=True)
        elif status == 'unavailable':
            products = products.filter(available=False)
        elif status == 'featured':
            products = products.filter(featured=True)
        elif status == 'low_stock':
            products = products.filter(stock__lt=5)
    
    # Paginación
    paginator = Paginator(products, 10)  # 10 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categorías para el filtro
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'section': 'products',
        'category_id': category_id,
        'search_query': search_query,
        'status': status
    }
    
    return render(request, 'dashboard/product_list.html', context)

@login_required
@user_passes_test(is_admin)
def product_detail(request, product_id):
    """Detalle y edición de producto"""
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Actualizar producto
        product.name = request.POST.get('name')
        product.category_id = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.available = 'available' in request.POST
        product.featured = 'featured' in request.POST
        
        product.save()
        
        # Manejar imágenes
        if 'image' in request.FILES:
            for image_file in request.FILES.getlist('image'):
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    is_main=False
                )
        
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('dashboard:product_detail', product_id=product.id)
    
    context = {
        'product': product,
        'categories': categories,
        'section': 'products'
    }
    
    return render(request, 'dashboard/product_detail.html', context)

@login_required
@user_passes_test(is_admin)
def product_create(request):
    """Crear nuevo producto"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        available = 'available' in request.POST
        featured = 'featured' in request.POST
        
        # Crear producto
        product = Product.objects.create(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            stock=stock,
            available=available,
            featured=featured
        )
        
        # Manejar imágenes
        if 'image' in request.FILES:
            for i, image_file in enumerate(request.FILES.getlist('image')):
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    is_main=(i == 0)  # Primera imagen como principal
                )
        
        messages.success(request, 'Producto creado correctamente.')
        return redirect('dashboard:product_detail', product_id=product.id)
    
    context = {
        'categories': categories,
        'section': 'products'
    }
    
    return render(request, 'dashboard/product_create.html', context)

@login_required
@user_passes_test(is_admin)
def order_list(request):
    """Lista de pedidos para administración"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Filtros
    status = request.GET.get('status')
    search_query = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status:
        orders = orders.filter(status=status)
    
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) | 
            Q(full_name__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Paginación
    paginator = Paginator(orders, 10)  # 10 pedidos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'section': 'orders',
        'status': status,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to
    }
    
    return render(request, 'dashboard/order_list.html', context)

@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    """Detalle y gestión de pedido"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        updated = False
        
        # Actualizar estado del pedido
        status = request.POST.get('status')
        if status and status != order.status:
            order.status = status
            order.save()
            updated = True
        
        # Actualizar información de envío
        shipping_status = request.POST.get('shipping_status')
        if shipping_status:
            order.shipping.status = shipping_status
            
            # Si el pedido se marca como enviado, registrar fecha
            if shipping_status == 'enviado' and not order.shipping.shipped_date:
                order.shipping.shipped_date = timezone.now()
            
            # Si el pedido se marca como entregado, registrar fecha
            if shipping_status == 'entregado' and not order.shipping.delivered_date:
                order.shipping.delivered_date = timezone.now()
            
            # Actualizar tracking y notas
            tracking_number = request.POST.get('tracking_number', '')
            carrier = request.POST.get('carrier', '')
            shipping_notes = request.POST.get('shipping_notes', '')
            
            if tracking_number != order.shipping.tracking_number:
                order.shipping.tracking_number = tracking_number
                updated = True
            
            if carrier != order.shipping.carrier:
                order.shipping.carrier = carrier
                updated = True
            
            if shipping_notes != order.shipping.notes:
                order.shipping.notes = shipping_notes
                updated = True
            
            order.shipping.save()
            updated = True
        
        # Actualizar información de pago
        payment_status = request.POST.get('payment_status')
        if payment_status:
            order.payment.status = payment_status
            
            # Si el pago se marca como completado, registrar fecha
            if payment_status == 'completado' and not order.payment.payment_date:
                order.payment.payment_date = timezone.now()
            
            # Actualizar transaction ID y notas
            transaction_id = request.POST.get('transaction_id', '')
            payment_notes = request.POST.get('payment_notes', '')
            
            if transaction_id != order.payment.transaction_id:
                order.payment.transaction_id = transaction_id
                updated = True
            
            if payment_notes != order.payment.notes:
                order.payment.notes = payment_notes
                updated = True
            
            order.payment.save()
            updated = True
        
        if updated:
            messages.success(request, 'Pedido actualizado correctamente.')
        else:
            messages.info(request, 'No se realizaron cambios.')
        
        return redirect('dashboard:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'section': 'orders'
    }
    
    return render(request, 'dashboard/order_detail.html', context)

@login_required
@user_passes_test(is_admin)
def category_list(request):
    """Lista de categorías para administración"""
    categories = Category.objects.all()
    
    # Agregar conteo de productos
    categories = categories.annotate(product_count=Count('products'))
    
    if request.method == 'POST':
        # Crear nueva categoría
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = 'is_active' in request.POST
        
        if name:
            category = Category.objects.create(
                name=name,
                description=description,
                is_active=is_active
            )
            
            # Manejar imagen
            if 'image' in request.FILES:
                category.image = request.FILES['image']
                category.save()
            
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('dashboard:category_list')
    
    context = {
        'categories': categories,
        'section': 'categories'
    }
    
    return render(request, 'dashboard/category_list.html', context)

@login_required
@user_passes_test(is_admin)
def category_detail(request, category_id):
    """Detalle y edición de categoría"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        # Actualizar categoría
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.is_active = 'is_active' in request.POST
        
        # Manejar imagen
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        
        category.save()
        
        messages.success(request, 'Categoría actualizada correctamente.')
        return redirect('dashboard:category_detail', category_id=category.id)
    
    # Productos de esta categoría
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
        'section': 'categories'
    }
    
    return render(request, 'dashboard/category_detail.html', context)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """Lista de usuarios para administración"""
    users = CustomUser.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    
    # Filtros
    search_query = request.GET.get('search')
    
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) | 
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(users, 10)  # 10 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'section': 'users',
        'search_query': search_query
    }
    
    return render(request, 'dashboard/user_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """Detalle de usuario y sus pedidos"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Obtener pedidos del usuario
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user_profile': user,
        'orders': orders,
        'section': 'users'
    }
    
    return render(request, 'dashboard/user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def update_product_image(request, image_id):
    """AJAX: Actualizar imagen de producto"""
    if request.method == 'POST':
        try:
            image = ProductImage.objects.get(id=image_id)
            action = request.POST.get('action')
            
            if action == 'make_main':
                # Desmarcar todas las imágenes principales del producto
                ProductImage.objects.filter(product=image.product, is_main=True).update(is_main=False)
                # Marcar esta como principal
                image.is_main = True
                image.save()
                return JsonResponse({'success': True})
            
            elif action == 'delete':
                # No eliminar si es la única imagen
                if image.product.images.count() > 1:
                    # Si es la principal, establecer otra como principal
                    if image.is_main:
                        next_image = image.product.images.exclude(id=image.id).first()
                        if next_image:
                            next_image.is_main = True
                            next_image.save()
                    
                    image.delete()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'No se puede eliminar la única imagen del producto.'})
            
        except ProductImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Imagen no encontrada.'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@login_required
@user_passes_test(is_admin)
def dashboard_settings(request):
    """Configuración general del panel"""
    return render(request, 'dashboard/settings.html', {'section': 'settings'})