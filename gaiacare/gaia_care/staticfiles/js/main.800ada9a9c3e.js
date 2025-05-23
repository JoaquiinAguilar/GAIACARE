// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Menú móvil
    const menuToggle = document.getElementById('menuToggle');
    const navDesktop = document.querySelector('.nav-desktop');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            if (navDesktop.style.display === 'flex') {
                navDesktop.style.display = 'none';
            } else {
                navDesktop.style.display = 'flex';
                navDesktop.style.position = 'absolute';
                navDesktop.style.top = '80px';
                navDesktop.style.left = '0';
                navDesktop.style.width = '100%';
                navDesktop.style.backgroundColor = '#fff';
                navDesktop.style.padding = '20px';
                navDesktop.style.boxShadow = '0 5px 10px rgba(0,0,0,0.1)';
                navDesktop.style.zIndex = '999';
                
                // Modificar estilo de la lista para móvil
                const navUl = navDesktop.querySelector('ul');
                navUl.style.flexDirection = 'column';
                
                // Modificar estilo de los ítems para móvil
                const navItems = navDesktop.querySelectorAll('li');
                navItems.forEach(item => {
                    item.style.margin = '10px 0';
                });
            }
        });
    }
    
    // Auto-ocultar mensajes después de 5 segundos
    const messages = document.querySelectorAll('.alert');
    if (messages.length > 0) {
        setTimeout(function() {
            messages.forEach(message => {
                // Crear un nuevo evento para Bootstrap 5
                const bsAlert = new bootstrap.Alert(message);
                bsAlert.close();
            });
        }, 5000);
    }
    
    // Cambio de imágenes en la vista de detalle de producto
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.querySelector('.main-image img');
    
    if (thumbnails.length > 0 && mainImage) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Cambiar la imagen principal
                const newSrc = this.querySelector('img').getAttribute('src');
                mainImage.setAttribute('src', newSrc);
                
                // Actualizar clase activa
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    // Botones de cantidad en página de producto
    const quantityInput = document.querySelector('.quantity-input input');
    const plusBtn = document.querySelector('.quantity-btn.plus');
    const minusBtn = document.querySelector('.quantity-btn.minus');
    
    if (quantityInput && plusBtn && minusBtn) {
        // Evitar que el input tenga valores negativos o cero
        quantityInput.addEventListener('change', function() {
            if (this.value < 1) {
                this.value = 1;
            }
        });
        
        // Botón para aumentar cantidad
        plusBtn.addEventListener('click', function() {
            const currentValue = parseInt(quantityInput.value);
            quantityInput.value = currentValue + 1;
        });
        
        // Botón para disminuir cantidad
        minusBtn.addEventListener('click', function() {
            const currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
    }
    
    // Formularios de agregar al carrito con AJAX
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    
    if (addToCartForms.length > 0) {
        addToCartForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Obtener datos del formulario
                const formData = new FormData(this);
                
                // Enviar petición AJAX
                fetch(this.getAttribute('action'), {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Actualizar contador del carrito
                        const cartCount = document.querySelector('.cart-count');
                        if (cartCount) {
                            cartCount.textContent = data.item_count;
                        } else {
                            // Si no existe el contador, crearlo
                            const cartIcon = document.querySelector('.cart-icon');
                            const span = document.createElement('span');
                            span.className = 'cart-count';
                            span.textContent = data.item_count;
                            cartIcon.appendChild(span);
                        }
                        
                        // Mostrar mensaje de éxito
                        showMessage('success', data.message);
                    } else {
                        // Mostrar mensaje de error
                        showMessage('danger', data.error);
                    }
                })
                .catch(error => {
                    showMessage('danger', 'Ha ocurrido un error. Inténtalo nuevamente.');
                    console.error('Error:', error);
                });
            });
        });
    }
    
    // Botones de actualizar carrito con AJAX
    const updateCartBtns = document.querySelectorAll('.update-cart-btn');
    
    if (updateCartBtns.length > 0) {
        updateCartBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const itemId = this.getAttribute('data-item-id');
                const action = this.getAttribute('data-action');
                
                // Crear FormData
                const formData = new FormData();
                formData.append('item_id', itemId);
                formData.append('action', action);
                
                // Obtener token CSRF
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Enviar petición AJAX
                fetch('/carrito/actualizar/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.removed) {
                            // Si se eliminó el item, remover la fila
                            const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
                            row.remove();
                            
                            // Si no quedan items, mostrar mensaje de carrito vacío
                            const tableBody = document.querySelector('tbody');
                            if (tableBody.children.length === 0) {
                                location.reload(); // Recargar para mostrar mensaje de carrito vacío
                            }
                        } else {
                            // Actualizar cantidad y total del item
                            const quantityEl = document.querySelector(`tr[data-item-id="${itemId}"] .cart-quantity-input`);
                            const itemTotalEl = document.querySelector(`tr[data-item-id="${itemId}"] .item-total`);
                            
                            if (quantityEl) quantityEl.value = data.quantity;
                            if (itemTotalEl) itemTotalEl.textContent = `$${data.item_total.toFixed(2)} MXN`;
                        }
                        
                        // Actualizar contador del carrito
                        const cartCount = document.querySelector('.cart-count');
                        if (cartCount) {
                            cartCount.textContent = data.item_count;
                            
                            // Si no hay items, quitar el contador
                            if (data.item_count === 0) {
                                cartCount.remove();
                            }
                        }
                        
                        // Actualizar total del carrito
                        const cartTotal = document.querySelector('.cart-summary-total .value');
                        if (cartTotal) {
                            cartTotal.textContent = `$${data.cart_total.toFixed(2)} MXN`;
                        }
                    } else {
                        // Mostrar mensaje de error
                        showMessage('danger', data.error);
                    }
                })
                .catch(error => {
                    showMessage('danger', 'Ha ocurrido un error. Inténtalo nuevamente.');
                    console.error('Error:', error);
                });
            });
        });
    }
    
    // Función para mostrar mensajes
    function showMessage(type, text) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${text}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const messagesContainer = document.querySelector('.messages-container');
        if (messagesContainer) {
            messagesContainer.appendChild(alertDiv);
            
            // Auto-ocultar después de 5 segundos
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }, 5000);
        }
    }
});