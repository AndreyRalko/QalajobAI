"""
Custom exception handler for DRF.
Returns consistent error responses.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'success': False,
            'message': _extract_message(response.data),
            'errors': response.data if isinstance(response.data, dict) else {'detail': response.data},
        }
        response.data = custom_data
        return response

    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return Response(
        {
            'success': False,
            'message': 'Internal server error',
            'errors': {},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_message(data):
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        if 'message' in data:
            return str(data['message'])
        for key, value in data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
            if isinstance(value, str):
                return f"{key}: {value}"
    if isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred'
