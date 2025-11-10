"""
Settings package for School Management System.
Import the appropriate settings module based on environment.
"""
import os

# Determine which settings to use
environment = os.getenv('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    from .base import *
