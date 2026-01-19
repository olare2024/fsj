# accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = "User Accounts"
    
    def ready(self):
        # Import signals to register them
        try:
            import accounts.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")