from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('sobre-nosotros/', views.AboutView.as_view(), name='about'),
    path('contacto/', views.ContactView.as_view(), name='contact'),
]