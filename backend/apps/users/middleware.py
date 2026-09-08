"""
QalaJob AI — Security and Logging Middleware.
Handles: request logging, banned user blocking, rate limiting headers, security headers.
"""

import json
import logging
import time

from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse

logger = logging.getLogger('apps')
security_logger = logging.getLogger('security')


class RequestLoggingMiddleware:
    """Logs request metadata for audit and performance monitoring."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        user = getattr(request, 'user', None)
        user_id = user.id if user and user.is_authenticated else 'anon'

        log_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'user': user_id,
            'duration_ms': round(duration * 1000, 2),
            'ip': self._get_client_ip(request),
        }

        if response.status_code >= 500:
            logger.error(f"SERVER_ERROR {log_data}")
        elif response.status_code in (401, 403):
            security_logger.warning(f"AUTH_FAILURE {log_data}")
        elif duration > 2.0:
            logger.warning(f"SLOW_REQUEST {log_data}")

        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class BannedUserMiddleware:
    """
    Block banned users from accessing API endpoints.
    Returns 403 for any authenticated request from a banned user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            try:
                profile = user.profile
                if getattr(profile, 'is_banned', False):
                    security_logger.warning(
                        f"BANNED_USER_ACCESS user={user.id} path={request.path} ip={self._get_ip(request)}"
                    )
                    if request.path.startswith('/api/'):
                        return JsonResponse(
                            {'message': 'Your account has been banned.', 'code': 'ACCOUNT_BANNED'},
                            status=403,
                        )
                    logout(request)
                    return HttpResponseRedirect('/login/?banned=1')
            except Exception:
                pass

        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    Applied after other middleware so it affects all responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent clickjacking
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # XSS protection
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Remove server header
        if 'Server' in response:
            del response['Server']

        # Permissions Policy
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        return response


class JSONPayloadSizeMiddleware:
    """
    Limit JSON request body size to prevent abuse.
    Max 5MB for regular requests, 10MB for file uploads.
    """

    MAX_BODY_SIZE = 5 * 1024 * 1024  # 5 MB
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        content_length = request.META.get('CONTENT_LENGTH')

        if content_length:
            try:
                size = int(content_length)
                content_type = request.content_type or ''

                limit = self.MAX_UPLOAD_SIZE if 'multipart' in content_type else self.MAX_BODY_SIZE

                if size > limit:
                    security_logger.warning(
                        f"PAYLOAD_TOO_LARGE size={size} limit={limit} path={request.path}"
                    )
                    return JsonResponse(
                        {'message': 'Request payload too large'},
                        status=413,
                    )
            except (ValueError, TypeError):
                pass

        return self.get_response(request)
