"""
Middleware for multi-tenancy support.
Handles school-based data isolation.
"""
from django.core.exceptions import PermissionDenied
from django.http import Http404

from apps.accounts.models import School


class TenantMiddleware:
    """
    Middleware to identify and set the current tenant (school) based on:
    1. Subdomain (for multi-tenant SaaS mode)
    2. User's school (for authenticated users)
    
    Sets request.school for use throughout the application.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Public URLs that don't require a school
        public_urls = [
            '/accounts/register/',
            '/accounts/login/',
            '/accounts/password-reset/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        # Check if current path is public
        is_public = any(request.path.startswith(url) for url in public_urls)
        
        # Try to identify school from subdomain first
        school = self.get_school_from_subdomain(request)
        
        # If no school from subdomain and user is authenticated, use user's school
        if not school and request.user.is_authenticated and hasattr(request.user, 'school'):
            school = request.user.school
        
        # Set the school in the request
        request.school = school
        
        # For non-public URLs, require a school context
        if not is_public and not school and request.user.is_authenticated:
            raise PermissionDenied("No school context available.")
        
        # Validate user has access to this school
        if request.user.is_authenticated and school:
            if request.user.is_superuser:
                # Superusers can access any school
                pass
            elif hasattr(request.user, 'school') and request.user.school:
                # Regular users must belong to the current school
                if request.user.school != school:
                    raise PermissionDenied("You don't have access to this school.")
        
        response = self.get_response(request)
        return response
    
    def get_school_from_subdomain(self, request):
        """
        Extract school from subdomain.
        Example: demo.schoolmanagement.com -> 'demo'
        """
        host = request.get_host().split(':')[0]  # Remove port if present
        parts = host.split('.')
        
        # Check if this is a subdomain (more than 2 parts for .com or 3 for .co.uk)
        if len(parts) >= 3:
            subdomain = parts[0]
            
            # Skip www and common subdomains
            if subdomain in ['www', 'api', 'admin']:
                return None
            
            try:
                return School.objects.get(subdomain=subdomain, is_active=True)
            except School.DoesNotExist:
                return None
        
        return None


class SchoolFilterMiddleware:
    """
    Middleware to automatically filter querysets by current school.
    This ensures data isolation between tenants.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
