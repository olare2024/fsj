# accounts/services/twilio_service.py

import logging
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from typing import Dict, Tuple, Optional

logger = logging.getLogger('accounts.twilio')  # Use specific logger


class TwilioService:
    """Enhanced Twilio service for SMS, voice OTP verification, and phone validation"""
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', 'AC9591dcdf19adece0de73451c2e1bd013')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')  # Set this in your environment
        self.verify_service_sid = getattr(settings, 'TWILIO_VERIFY_SERVICE_SID', 'VAb2e2e72c651a7728fc734d21dc1a4ab5')
        self.from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')  # Your Twilio phone number
        self.enabled = getattr(settings, 'TWILIO_ENABLED', False)
        
        # Initialize Twilio client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twilio client with proper error handling"""
        if not self.enabled:
            logger.warning("Twilio service is disabled in settings")
            return
            
        if not self.account_sid or not self.auth_token:
            logger.error("Twilio credentials missing: ACCOUNT_SID or AUTH_TOKEN not set")
            return
            
        try:
            self.client = Client(self.account_sid, self.auth_token)
            # Test the client with a simple operation
            self.client.api.accounts(self.account_sid).fetch()
            logger.info("Twilio client initialized and authenticated successfully")
            
        except TwilioRestException as e:
            logger.error(f"Twilio authentication failed: {e.code} - {e.msg}")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.client = None
    
    def is_operational(self) -> bool:
        """Check if Twilio service is operational"""
        return self.enabled and self.client is not None
    
    def send_verification_sms(self, phone_number: str, custom_message: str = None) -> Tuple[bool, str]:
        """
        Send SMS verification code using Twilio Verify API
        
        Args:
            phone_number: The phone number to send verification to
            custom_message: Optional custom message for verification
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_operational():
            logger.error("Twilio service not operational")
            return False, "Twilio service not available"
        
        try:
            # Prepare verification parameters
            verification_params = {
                'to': phone_number,
                'channel': 'sms'
            }
            
            # Add custom message if provided
            if custom_message:
                verification_params['custom_message'] = custom_message
            
            verification = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verifications \
                .create(**verification_params)
            
            logger.info(f"Twilio verification SMS sent to {phone_number}: SID {verification.sid}")
            return True, verification.sid
            
        except TwilioRestException as e:
            error_msg = self._parse_twilio_error(e)
            logger.error(f"Twilio SMS error for {phone_number}: {error_msg}")
            return False, error_msg
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {phone_number}: {str(e)}")
            return False, f"Service temporarily unavailable: {str(e)}"
    
    def send_verification_voice(self, phone_number: str) -> Tuple[bool, str]:
        """
        Send voice verification call using Twilio Verify API
        
        Args:
            phone_number: The phone number to call
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_operational():
            logger.error("Twilio service not operational")
            return False, "Twilio service not available"
        
        try:
            verification = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verifications \
                .create(to=phone_number, channel='call')
            
            logger.info(f"Twilio verification voice call to {phone_number}: SID {verification.sid}")
            return True, verification.sid
            
        except TwilioRestException as e:
            error_msg = self._parse_twilio_error(e)
            logger.error(f"Twilio voice error for {phone_number}: {error_msg}")
            return False, error_msg
        except Exception as e:
            logger.error(f"Unexpected error with voice call to {phone_number}: {str(e)}")
            return False, f"Service temporarily unavailable: {str(e)}"
    
    def verify_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """
        Verify the code sent via SMS or voice
        
        Args:
            phone_number: The phone number to verify
            code: The verification code entered by user
            
        Returns:
            Tuple of (is_verified: bool, status_message: str)
        """
        if not self.is_operational():
            logger.error("Twilio service not operational")
            return False, "Twilio service not available"
        
        if not code or len(code) < 4:
            return False, "Invalid verification code format"
        
        try:
            verification_check = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verification_checks \
                .create(to=phone_number, code=code.strip())
            
            is_approved = verification_check.status == 'approved'
            status_msg = verification_check.status
            
            log_level = logging.INFO if is_approved else logging.WARNING
            logger.log(log_level, f"Twilio verification for {phone_number}: {status_msg}")
            
            return is_approved, status_msg
            
        except TwilioRestException as e:
            error_msg = self._parse_twilio_error(e)
            logger.error(f"Twilio verification error for {phone_number}: {error_msg}")
            return False, error_msg
        except Exception as e:
            logger.error(f"Unexpected verification error for {phone_number}: {str(e)}")
            return False, f"Verification service temporarily unavailable: {str(e)}"
    
    def validate_phone_number(self, phone_number: str) -> Dict:
        """
        Validate phone number using Twilio Lookup API
        
        Args:
            phone_number: The phone number to validate
            
        Returns:
            Dictionary with validation results
        """
        if not self.is_operational():
            return {
                'valid': False, 
                'error': 'Twilio service not available',
                'phone_number': phone_number
            }
        
        try:
            phone_number_info = self.client.lookups \
                .v2 \
                .phone_numbers(phone_number) \
                .fetch(fields='line_type_intelligence,carrier,caller_name')
            
            result = {
                'valid': True,
                'phone_number': phone_number_info.phone_number,
                'national_format': phone_number_info.national_format,
                'country_code': phone_number_info.country_code,
                'validation_timestamp': timezone.now().isoformat(),
            }
            
            # Add carrier information if available
            if hasattr(phone_number_info, 'carrier'):
                result['carrier'] = {
                    'name': phone_number_info.carrier.get('name', ''),
                    'type': phone_number_info.carrier.get('type', ''),
                    'mobile_network_code': phone_number_info.carrier.get('mobile_network_code', ''),
                    'mobile_country_code': phone_number_info.carrier.get('mobile_country_code', ''),
                }
            
            # Add line type intelligence
            if hasattr(phone_number_info, 'line_type_intelligence'):
                result['line_type'] = phone_number_info.line_type_intelligence.get('type', 'unknown')
            
            logger.info(f"Phone number validation successful for {phone_number}")
            return result
            
        except TwilioRestException as e:
            error_msg = self._parse_twilio_error(e)
            logger.warning(f"Twilio phone validation failed for {phone_number}: {error_msg}")
            return {
                'valid': False, 
                'error': error_msg,
                'phone_number': phone_number
            }
        except Exception as e:
            logger.error(f"Unexpected phone validation error for {phone_number}: {str(e)}")
            return {
                'valid': False, 
                'error': f"Validation service unavailable: {str(e)}",
                'phone_number': phone_number
            }
    
    def send_direct_sms(self, to_number: str, message: str) -> Tuple[bool, str]:
        """
        Send direct SMS message (not through Verify API)
        
        Args:
            to_number: Recipient phone number
            message: SMS message content
            
        Returns:
            Tuple of (success: bool, message_sid: str)
        """
        if not self.is_operational():
            return False, "Twilio service not available"
        
        if not self.from_number:
            return False, "Twilio phone number not configured"
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"Direct SMS sent to {to_number}: SID {message_obj.sid}")
            return True, message_obj.sid
            
        except TwilioRestException as e:
            error_msg = self._parse_twilio_error(e)
            logger.error(f"Twilio direct SMS error to {to_number}: {error_msg}")
            return False, error_msg
        except Exception as e:
            logger.error(f"Unexpected error sending direct SMS to {to_number}: {str(e)}")
            return False, f"SMS service temporarily unavailable: {str(e)}"
    
    def _parse_twilio_error(self, error: TwilioRestException) -> str:
        """
        Parse Twilio REST exception and return user-friendly error message
        
        Args:
            error: TwilioRestException instance
            
        Returns:
            User-friendly error message
        """
        error_mappings = {
            20404: "Verification service not found. Please contact support.",
            60200: "Invalid phone number format.",
            60203: "Maximum verification attempts reached. Please try again later.",
            60212: "Too many verification attempts. Please wait before trying again.",
            60606: "Phone number is blacklisted or invalid.",
            21408: "Permission denied for verification service.",
            21211: "Invalid phone number format.",
            21610: "Phone number cannot receive SMS messages.",
        }
        
        # Return mapped message or generic error
        return error_mappings.get(error.code, f"Verification error: {error.msg}")
    
    def get_verification_status(self, verification_sid: str) -> Optional[Dict]:
        """
        Get the status of a verification attempt
        
        Args:
            verification_sid: The verification SID from send_verification_* methods
            
        Returns:
            Dictionary with verification status or None if error
        """
        if not self.is_operational():
            return None
        
        try:
            verification = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verifications(verification_sid) \
                .fetch()
            
            return {
                'sid': verification.sid,
                'status': verification.status,
                'to': verification.to,
                'channel': verification.channel,
                'date_created': verification.date_created.isoformat() if verification.date_created else None,
                'date_updated': verification.date_updated.isoformat() if verification.date_updated else None,
            }
        except Exception as e:
            logger.error(f"Error fetching verification status for {verification_sid}: {str(e)}")
            return None


# Singleton instance with lazy initialization
_twilio_service_instance = None

def get_twilio_service() -> TwilioService:
    """Get or create Twilio service singleton instance"""
    global _twilio_service_instance
    if _twilio_service_instance is None:
        _twilio_service_instance = TwilioService()
    return _twilio_service_instance


# Backward compatibility
twilio_service = get_twilio_service()