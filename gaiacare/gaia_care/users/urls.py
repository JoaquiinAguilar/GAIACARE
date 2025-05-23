from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('perfil/', views.ProfileView.as_view(), name='profile'),
]