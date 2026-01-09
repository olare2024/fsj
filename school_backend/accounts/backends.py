# apps/accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend for email-only authentication.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to get email from different possible parameters
        email = kwargs.get('email') or username
        
        # Use simple logging without emojis to avoid encoding issues
        logger.info(f"Authentication attempt - Email: {email}, Username param: {username}")
        
        if not email or not password:
            logger.warning("Missing email or password")
            return None
            
        try:
            # Normalize email
            email = email.lower().strip()
            
            # Try to fetch user by email only (since your model doesn't have username)
            user = User.objects.get(email__iexact=email)
            
            # FIXED: Use email instead of username since your model doesn't have username field
            logger.info(f"User found: {user.email} (Active: {user.is_active})")
            
            # Check password
            if not user.check_password(password):
                logger.warning(f"Password check failed for: {email}")
                return None
            
            # Check if user can authenticate
            if not self.user_can_authenticate(user):
                logger.warning(f"User cannot authenticate: {user.email} - Active: {user.is_active}")
                return None
                
            logger.info(f"Authentication successful for: {user.email}")
            return user
                
        except User.DoesNotExist:
            logger.warning(f"User not found: {email}")
            return None
        except User.MultipleObjectsReturned:
            logger.warning(f"Multiple users found for: {email}")
            users = User.objects.filter(email__iexact=email)
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            return None
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return None
    
    def user_can_authenticate(self, user):
        """
        Check if the user can authenticate (only check is_active)
        """
        is_active = getattr(user, 'is_active', None)
        
        logger.info(f"User auth check - Active: {is_active}")
        
        # User can authenticate only if active
        return is_active

    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None