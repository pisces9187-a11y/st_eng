"""
JWT Authentication Middleware for Template Views.
Validates JWT tokens from cookies or Authorization header for protected pages.
Automatically refreshes expired tokens using refresh token.
"""

from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
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
        request.should_clear_cookies = False
        
        token = self._get_token(request)
        
        if token:
            try:
                validated_token = self.jwt_auth.get_validated_token(token)
                user = self.jwt_auth.get_user(validated_token)
                request.jwt_user = user
                request.jwt_authenticated = True
                request.user = user
                logger.debug(f"JWT authentication successful for user {user.username}")
            except (InvalidToken, TokenError) as e:
                logger.info(f"Access token invalid/expired: {str(e)[:100]}")
                # Try to refresh token if refresh token exists
                refresh_token = request.COOKIES.get('refresh_token')
                if refresh_token:
                    logger.info("Attempting to refresh token...")
                    try:
                        new_tokens = self._refresh_access_token(refresh_token)
                        if new_tokens:
                            token = new_tokens['access']
                            validated_token = self.jwt_auth.get_validated_token(token)
                            user = self.jwt_auth.get_user(validated_token)
                            request.jwt_user = user
                            request.jwt_authenticated = True
                            request.user = user
                            request.new_tokens = new_tokens  # Pass to response for cookie update
                            logger.info(f"Token refreshed successfully for user {user.username}")
                        else:
                            logger.warning("Token refresh failed - clearing cookies")
                            request.should_clear_cookies = True
                    except Exception as e:
                        logger.warning(f"Token refresh exception: {str(e)[:100]}")
                        request.should_clear_cookies = True
                else:
                    logger.info("No refresh token found - clearing cookies")
                    request.should_clear_cookies = True
        
        response = self.get_response(request)
        
        # Clear invalid cookies if needed
        if request.should_clear_cookies:
            logger.info("Clearing invalid authentication cookies")
            response.delete_cookie('access_token', samesite='Lax')
            response.delete_cookie('refresh_token', samesite='Lax')
        
        # Update cookies with new tokens if refreshed
        if hasattr(request, 'new_tokens'):
            logger.info("Updating cookies with refreshed tokens")
            response.set_cookie(
                'access_token',
                request.new_tokens['access'],
                max_age=86400,  # 24 hours
                httponly=True,
                secure=False,  # Set to True in production
                samesite='Lax'
            )
            response.set_cookie(
                'refresh_token',
                request.new_tokens['refresh'],
                max_age=2592000,  # 30 days
                httponly=True,
                secure=False,  # Set to True in production
                samesite='Lax'
            )
        
        return response
    
    def _get_token(self, request):
        """Extract JWT token from request."""
        # Try Authorization header first
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # Try cookie
        return request.COOKIES.get('access_token')
    
    def _refresh_access_token(self, refresh_token_str):
        """Refresh access token using refresh token."""
        try:
            refresh = RefreshToken(refresh_token_str)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        except Exception as e:
            logger.debug(f"Could not refresh token: {e}")
            return None


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
