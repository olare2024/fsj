# accounts/services/twilio_service.py

import logging
from typing import Dict, Tuple, Optional

from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger("accounts.twilio")


class TwilioService:
    """
    Twilio service for SMS, voice OTP verification, phone validation,
    and direct messaging using environment-based configuration.
    """

    def __init__(self):
        # Load configuration strictly from settings / environment
        self.account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        self.auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        self.verify_service_sid = getattr(settings, "TWILIO_VERIFY_SERVICE_SID", None)
        self.from_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)
        self.enabled = getattr(settings, "TWILIO_ENABLED", False)

        self.client: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Twilio client safely."""
        if not self.enabled:
            logger.warning("Twilio service is disabled via settings.")
            return

        if not all([self.account_sid, self.auth_token]):
            logger.error("Twilio credentials are missing in environment variables.")
            return

        try:
            self.client = Client(self.account_sid, self.auth_token)
            self.client.api.accounts(self.account_sid).fetch()
            logger.info("Twilio client initialized successfully.")

        except TwilioRestException as exc:
            logger.error(
                "Twilio authentication failed (%s): %s",
                exc.code,
                exc.msg,
            )
            self.client = None
        except Exception as exc:
            logger.exception("Unexpected error initializing Twilio client: %s", exc)
            self.client = None

    def is_operational(self) -> bool:
        """Return True if Twilio is enabled and authenticated."""
        return self.enabled and self.client is not None

    # ------------------------------------------------------------------
    # Verification (SMS / Voice)
    # ------------------------------------------------------------------

    def send_verification_sms(
        self, phone_number: str, custom_message: Optional[str] = None
    ) -> Tuple[bool, str]:
        if not self.is_operational():
            return False, "Twilio service not available"

        try:
            params = {"to": phone_number, "channel": "sms"}
            if custom_message:
                params["custom_message"] = custom_message

            verification = (
                self.client.verify.v2.services(self.verify_service_sid)
                .verifications.create(**params)
            )

            logger.info("Verification SMS sent to %s (SID: %s)", phone_number, verification.sid)
            return True, verification.sid

        except TwilioRestException as exc:
            message = self._parse_twilio_error(exc)
            logger.error("SMS verification failed for %s: %s", phone_number, message)
            return False, message
        except Exception as exc:
            logger.exception("Unexpected SMS error: %s", exc)
            return False, "Verification service temporarily unavailable"

    def send_verification_voice(self, phone_number: str) -> Tuple[bool, str]:
        if not self.is_operational():
            return False, "Twilio service not available"

        try:
            verification = (
                self.client.verify.v2.services(self.verify_service_sid)
                .verifications.create(to=phone_number, channel="call")
            )

            logger.info("Verification voice call placed to %s (SID: %s)", phone_number, verification.sid)
            return True, verification.sid

        except TwilioRestException as exc:
            message = self._parse_twilio_error(exc)
            logger.error("Voice verification failed for %s: %s", phone_number, message)
            return False, message
        except Exception as exc:
            logger.exception("Unexpected voice error: %s", exc)
            return False, "Verification service temporarily unavailable"

    def verify_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        if not self.is_operational():
            return False, "Twilio service not available"

        if not code or len(code.strip()) < 4:
            return False, "Invalid verification code"

        try:
            check = (
                self.client.verify.v2.services(self.verify_service_sid)
                .verification_checks.create(to=phone_number, code=code.strip())
            )

            approved = check.status == "approved"
            logger.info("Verification result for %s: %s", phone_number, check.status)
            return approved, check.status

        except TwilioRestException as exc:
            message = self._parse_twilio_error(exc)
            logger.error("Code verification failed for %s: %s", phone_number, message)
            return False, message
        except Exception as exc:
            logger.exception("Unexpected verification error: %s", exc)
            return False, "Verification service temporarily unavailable"

    # ------------------------------------------------------------------
    # Phone validation
    # ------------------------------------------------------------------

    def validate_phone_number(self, phone_number: str) -> Dict:
        if not self.is_operational():
            return {
                "valid": False,
                "error": "Twilio service not available",
                "phone_number": phone_number,
            }

        try:
            info = (
                self.client.lookups.v2.phone_numbers(phone_number)
                .fetch(fields="line_type_intelligence,carrier")
            )

            result = {
                "valid": True,
                "phone_number": info.phone_number,
                "national_format": info.national_format,
                "country_code": info.country_code,
                "validation_timestamp": timezone.now().isoformat(),
            }

            if hasattr(info, "carrier") and info.carrier:
                result["carrier"] = info.carrier

            if hasattr(info, "line_type_intelligence") and info.line_type_intelligence:
                result["line_type"] = info.line_type_intelligence.get("type", "unknown")

            logger.info("Phone number validation successful for %s", phone_number)
            return result

        except TwilioRestException as exc:
            message = self._parse_twilio_error(exc)
            logger.warning("Phone validation failed for %s: %s", phone_number, message)
            return {"valid": False, "error": message, "phone_number": phone_number}
        except Exception as exc:
            logger.exception("Unexpected phone validation error: %s", exc)
            return {
                "valid": False,
                "error": "Validation service unavailable",
                "phone_number": phone_number,
            }

    # ------------------------------------------------------------------
    # Direct SMS
    # ------------------------------------------------------------------

    def send_direct_sms(self, to_number: str, message: str) -> Tuple[bool, str]:
        if not self.is_operational():
            return False, "Twilio service not available"

        if not self.from_number:
            return False, "Twilio phone number not configured"

        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number,
            )

            logger.info("Direct SMS sent to %s (SID: %s)", to_number, msg.sid)
            return True, msg.sid

        except TwilioRestException as exc:
            message = self._parse_twilio_error(exc)
            logger.error("Direct SMS failed for %s: %s", to_number, message)
            return False, message
        except Exception as exc:
            logger.exception("Unexpected SMS error: %s", exc)
            return False, "SMS service temporarily unavailable"

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_twilio_error(error: TwilioRestException) -> str:
        error_map = {
            20404: "Verification service not found.",
            60200: "Invalid phone number format.",
            60203: "Maximum verification attempts reached.",
            60212: "Too many verification attempts. Try again later.",
            60606: "Phone number is blacklisted or invalid.",
            21408: "Permission denied for verification service.",
            21211: "Invalid phone number.",
            21610: "Phone number cannot receive SMS.",
        }

        return error_map.get(error.code, f"Twilio error: {error.msg}")


# ----------------------------------------------------------------------
# Singleton accessor
# ----------------------------------------------------------------------

_twilio_service_instance: Optional[TwilioService] = None


def get_twilio_service() -> TwilioService:
    global _twilio_service_instance
    if _twilio_service_instance is None:
        _twilio_service_instance = TwilioService()
    return _twilio_service_instance


# Backward compatibility
twilio_service = get_twilio_service()
