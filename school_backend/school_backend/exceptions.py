from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': {
                'code': response.status_code,
                'message': response.data.get('detail', 'An error occurred'),
                'details': response.data
            }
        }
    else:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        response = Response(
            {
                'error': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': 'An internal server error occurred',
                    'details': str(exc) if DEBUG else None
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response