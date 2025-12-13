"""
JWT Authentication Middleware for Template Views.
Validates JWT tokens from cookies or Authorization header for protected pages.
"""

from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    """
    Middleware that authenticates users via JWT token.
    Sets request.jwt_user if valid token is found.
    
    Token can be provided via:
    1. Authorization header: Bearer <token>
    2. Cookie: access_token=<token>
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()
    
    def __call__(self, request):
        # Try to authenticate via JWT
        request.jwt_user = None
        request.jwt_authenticated = False
        
        token = self._get_token(request)
        
        if token:
            try:
                validated_token = self.jwt_auth.get_validated_token(token)
                user = self.jwt_auth.get_user(validated_token)
                request.jwt_user = user
                request.jwt_authenticated = True
                # Also set request.user for compatibility
                request.user = user
            except (InvalidToken, TokenError) as e:
                logger.debug(f"JWT validation failed: {e}")
                request.jwt_authenticated = False
        
        response = self.get_response(request)
        return response
    
    def _get_token(self, request):
        """Extract JWT token from request."""
        # Try Authorization header first
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # Try cookie
        return request.COOKIES.get('access_token')


class JWTRequiredMixin:
    """
    Mixin for class-based views that require JWT authentication.
    Redirects to login page if not authenticated.
    
    For API endpoints, returns 401 JSON response.
    For page views, redirects to login with ?next= parameter.
    """
    login_url = None
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated via JWT
        if not getattr(request, 'jwt_authenticated', False):
            # For AJAX/API requests, return 401
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Authentication required',
                    'code': 'not_authenticated'
                }, status=401)
            
            # For page requests, redirect to login
            login_url = self.login_url or reverse('users:login')
            next_url = request.get_full_path()
            return redirect(f'{login_url}?next={next_url}')
        
        return super().dispatch(request, *args, **kwargs)


def jwt_required(view_func):
    """
    Decorator for function-based views that require JWT authentication.
    """
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'jwt_authenticated', False):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Authentication required',
                    'code': 'not_authenticated'
                }, status=401)
            
            login_url = reverse('users:login')
            next_url = request.get_full_path()
            return redirect(f'{login_url}?next={next_url}')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
