from django.shortcuts import render, redirect
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import CustomUser, UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm

class ProfileView(LoginRequiredMixin, TemplateView):
    """Vista del perfil de usuario"""
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserUpdateForm(instance=self.request.user)
        context['profile_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        return context
    
    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('users:profile')
        
        context = self.get_context_data(**kwargs)
        context['user_form'] = user_form
        context['profile_form'] = profile_form
        return render(request, self.template_name, context)