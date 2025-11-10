"""
Custom authentication backends for the school management system.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import School
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class SchoolAuthenticationBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login using:
    1. School name + their email + password
    2. School name + their username + password
    
    Format: school_name/email or school_name/username
    Example: "Happy Academy/john@example.com" or "Happy Academy/john"
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Check if username contains school name separator
        if '/' not in username:
            # Don't handle this case - let other backends handle it
            return None
        
        # Split school name and user identifier
        try:
            school_name, user_identifier = username.split('/', 1)
            school_name = school_name.strip()
            user_identifier = user_identifier.strip()
        except ValueError:
            logger.debug(f"Failed to split username: {username}")
            return None
        
        logger.debug(f"School-based auth attempt: school='{school_name}', user='{user_identifier}'")
        
        # Find the school
        try:
            school = School.objects.get(
                Q(name__iexact=school_name) | Q(subdomain__iexact=school_name)
            )
            logger.debug(f"Found school: {school.name} (ID: {school.id})")
        except School.DoesNotExist:
            logger.debug(f"School not found: '{school_name}'")
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        
        # Find the user by email or username in that school
        try:
            user = User.objects.get(
                Q(email__iexact=user_identifier) | Q(username__iexact=user_identifier),
                school=school
            )
            logger.debug(f"Found user: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            logger.debug(f"User not found in school: '{user_identifier}'")
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            logger.debug(f"Multiple users found for: '{user_identifier}'")
            # Multiple users found - try to narrow down
            user = User.objects.filter(
                Q(email__iexact=user_identifier) | Q(username__iexact=user_identifier),
                school=school
            ).first()
            if not user:
                return None
        
        # Check password and user status
        if user.check_password(password):
            logger.debug(f"Password check passed for user: {user.username}")
            if self.user_can_authenticate(user):
                logger.debug(f"User can authenticate: {user.username}")
                return user
            else:
                logger.debug(f"User cannot authenticate (inactive?): {user.username}")
        else:
            logger.debug(f"Password check failed for user: {user.username}")
        
        return None


class EmailOrUsernameBackend(ModelBackend):
    """
    Fallback authentication backend that allows login with email or username
    without requiring school name. Useful for superusers and single-school setups.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Try to find user by email or username
        try:
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Multiple users found - return None for security
            return None
        
        # Check password and user status
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
