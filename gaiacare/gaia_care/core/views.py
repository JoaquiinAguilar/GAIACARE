from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.views import View
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from products.models import Product, Category

class HomeView(TemplateView):
    """Vista para la página principal"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener productos destacados
        context['featured_products'] = Product.objects.filter(featured=True, available=True)[:3]
        # Obtener categorías activas
        context['categories'] = Category.objects.filter(is_active=True)[:4]
        return context

class AboutView(TemplateView):
    """Vista para la página Sobre Nosotros"""
    template_name = 'core/about.html'

class ContactView(View):
    """Vista para la página de Contacto"""
    template_name = 'core/contact.html'
    
    def get(self, request):
        """Mostrar el formulario de contacto"""
        return render(request, self.template_name)
    
    def post(self, request):
        """Procesar el formulario de contacto"""
        # Obtener datos del formulario
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        privacy = request.POST.get('privacy')
        
        # Validar que todos los campos estén completos
        if not all([name, email, subject, message, privacy]):
            messages.error(request, 'Por favor, completa todos los campos del formulario.')
            return render(request, self.template_name)
        
        # Preparar el contenido del correo
        email_subject = f'[Contacto GaiaCare] {subject}'
        email_body = f"""
Nuevo mensaje de contacto de GaiaCare

Nombre: {name}
Email: {email}
Asunto: {subject}

Mensaje:
{message}

---
Este mensaje fue enviado desde el formulario de contacto de GaiaCare.
        """
        
        try:
            # Enviar correo
            send_mail(
                email_subject,
                email_body,
                email,  # From email
                ['hola@gaiacare.mx'],  # To email
                fail_silently=False,
            )
            
            messages.success(
                request, 
                '¡Gracias por contactarnos! Tu mensaje ha sido enviado correctamente. '
                'Te responderemos a la brevedad.'
            )
            return redirect('core:contact')
            
        except Exception as e:
            messages.error(
                request, 
                'Hubo un error al enviar tu mensaje. Por favor, intenta nuevamente '
                'o contáctanos directamente a hola@gaiacare.mx'
            )
            return render(request, self.template_name)