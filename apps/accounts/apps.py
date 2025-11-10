from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Accounts & Users'
    
    def ready(self):
        """Import signals when app is ready."""
        pass  # Import signals here when we add them
