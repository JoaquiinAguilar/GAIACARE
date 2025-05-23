from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
import json

from .models import ProductImage, Product, ProductAttribute, ProductAttributeValue

@staff_member_required
@require_POST
def make_main_image(request, image_id):
    """Vista para establecer una imagen como principal"""
    try:
        image = get_object_or_404(ProductImage, id=image_id)
        product = image.product
        
        # Desmarcar cualquier otra imagen principal
        ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)
        
        # Marcar esta imagen como principal
        image.is_main = True
        image.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
@require_POST
def reorder_images(request):
    """Vista para reordenar imágenes de producto"""
    try:
        image_ids = json.loads(request.POST.get('image_ids', '[]'))
        
        for order, image_id in enumerate(image_ids):
            ProductImage.objects.filter(id=image_id).update(order=order)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
def get_attributes_for_category(request, category_id):
    """Vista para obtener atributos basados en una categoría"""
    try:
        # Obtener todos los atributos disponibles
        attributes = ProductAttribute.objects.all()
        
        # Formato para respuesta JSON
        attributes_data = []
        for attr in attributes:
            # Obtener valores utilizados para este atributo
            values_used = ProductAttributeValue.objects.filter(
                attribute=attr,
                product__category_id=category_id
            ).values_list('value', flat=True).distinct()
            
            # Si no hay valores usados, proporcionar algunos predeterminados según el atributo
            if not values_used:
                if attr.name == 'Aroma':
                    default_values = ['Floral', 'Cítrico', 'Dulce', 'Herbal', 'Amaderado']
                elif attr.name == 'Tamaño':
                    default_values = ['30g', '50g', '100g']
                elif attr.name == 'Duración':
                    default_values = ['2-3 horas', '4-6 horas', '8+ horas']
                elif attr.name == 'Intensidad':
                    default_values = ['Suave', 'Media', 'Fuerte']
                else:
                    default_values = []
                
                values_used = default_values
            
            attributes_data.append({
                'id': attr.id,
                'name': attr.name,
                'values': list(values_used)
            })
        
        return JsonResponse({'success': True, 'attributes': attributes_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})