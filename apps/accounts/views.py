from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import SchoolRegistrationForm, SchoolLoginForm


class SchoolRegistrationView(CreateView):
    """
    Public school registration view.
    Creates a new school and its admin user.
    """
    form_class = SchoolRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard:index')
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to dashboard
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Save the school and log in the admin user"""
        response = super().form_valid(form)
        
        # Get the newly created admin user
        admin_user = self.object.users.filter(role='admin').first()
        
        if admin_user:
            # Log in the admin user
            login(self.request, admin_user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(
                self.request,
                f'Welcome to {self.object.name}! Your school has been successfully registered.'
            )
        
        return response
    
    def form_invalid(self, form):
        """Handle form errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """
    Custom login view with school-based authentication
    Supports: school_name/email or just email
    """
    template_name = 'accounts/login.html'
    form_class = SchoolLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        return reverse_lazy('dashboard:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any custom context data here
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view
    """
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Profile'
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    """
    School settings view (admin only)
    """
    template_name = 'accounts/settings.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Only allow admin users
        if request.user.role != 'admin':
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'School Settings'
        return context
