from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User Accounts'

    def ready(self):
        # Import signals only after the app is ready
        try:
            import accounts.signals
        except ImportError:
            # Silently fail if signals module doesn't exist
            pass