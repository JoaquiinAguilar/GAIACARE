(function($) {
    $(document).ready(function() {
        // Ajuste para la vista previa de imágenes al subirlas
        $('.field-image input[type="file"]').change(function() {
            const file = this.files[0];
            const fieldset = $(this).closest('fieldset');
            const previewDiv = fieldset.find('.image_preview');
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (previewDiv.length) {
                        previewDiv.html('<img src="' + e.target.result + '" style="max-width: 300px; max-height: 200px;">');
                    } else {
                        $('<div class="image_preview"><img src="' + e.target.result + '" style="max-width: 300px; max-height: 200px;"></div>').insertAfter($(this).closest('.form-row'));
                    }
                };
                reader.readAsDataURL(file);
            }
        });
        
        // Marca una imagen como principal
        $('.make-main-image').click(function(e) {
            e.preventDefault();
            
            const form = $(this).closest('form');
            const imageId = $(this).data('image-id');
            const csrfToken = form.find('input[name="csrfmiddlewaretoken"]').val();
            
            $.ajax({
                url: '/admin/products/productimage/' + imageId + '/make-main/',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': csrfToken
                },
                success: function(response) {
                    if (response.success) {
                        // Actualiza la interfaz para mostrar la nueva imagen principal
                        $('.main-image-indicator').remove();
                        $('.make-main-image').show();
                        
                        // Marca la imagen seleccionada como principal
                        const selectedImageRow = $('#image_' + imageId);
                        selectedImageRow.find('.make-main-image').hide();
                        $('<span class="main-image-indicator" style="color: green; margin-left: 10px;"><i class="fas fa-check"></i> Imagen Principal</span>').insertAfter(selectedImageRow.find('.make-main-image'));
                        
                        // Muestra mensaje de éxito
                        alert('Imagen establecida como principal');
                    } else {
                        alert('Error al establecer la imagen como principal: ' + response.error);
                    }
                },
                error: function() {
                    alert('Error de comunicación con el servidor');
                }
            });
        });
        
        // Permite reordenar imágenes mediante drag & drop
        if ($('#product-images-table tbody').length) {
            $('#product-images-table tbody').sortable({
                axis: 'y',
                handle: '.move-handle',
                update: function(event, ui) {
                    const imageIds = [];
                    $('#product-images-table tbody tr').each(function() {
                        imageIds.push($(this).data('image-id'));
                    });
                    
                    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
                    
                    $.ajax({
                        url: '/admin/products/reorder-images/',
                        type: 'POST',
                        data: {
                            'csrfmiddlewaretoken': csrfToken,
                            'image_ids': JSON.stringify(imageIds)
                        },
                        success: function(response) {
                            if (!response.success) {
                                alert('Error al reordenar imágenes: ' + response.error);
                            }
                        },
                        error: function() {
                            alert('Error de comunicación con el servidor');
                        }
                    });
                }
            });
        }
        
        // Ajustes para las categorías
        $('#id_category').change(function() {
            const categoryId = $(this).val();
            if (categoryId) {
                // Si se selecciona una categoría, cargar atributos relacionados
                loadAttributeOptions(categoryId);
            }
        });
        
        function loadAttributeOptions(categoryId) {
            $.ajax({
                url: '/admin/products/get-attributes/' + categoryId + '/',
                type: 'GET',
                success: function(response) {
                    if (response.attributes) {
                        // Actualizar los campos de atributos disponibles
                        const attributeContainer = $('#attribute-values-container');
                        
                        // Limpiar contenedor anterior
                        attributeContainer.empty();
                        
                        // Agregar nuevos campos de atributos
                        response.attributes.forEach(function(attr) {
                            const fieldHtml = `
                                <div class="form-row attribute-row">
                                    <div class="field-box">
                                        <label>${attr.name}:</label>
                                        <select name="attribute_${attr.id}" class="form-control">
                                            <option value="">---------</option>
                                            ${attr.values.map(val => `<option value="${val}">${val}</option>`).join('')}
                                        </select>
                                    </div>
                                </div>
                            `;
                            attributeContainer.append(fieldHtml);
                        });
                    }
                },
                error: function() {
                    console.error('Error al cargar los atributos para la categoría');
                }
            });
        }
        
        // Si ya hay una categoría seleccionada al cargar la página
        const initialCategory = $('#id_category').val();
        if (initialCategory) {
            loadAttributeOptions(initialCategory);
        }
    });
})(django.jQuery);