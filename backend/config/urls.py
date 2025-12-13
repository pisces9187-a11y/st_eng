"""
URL configuration for English Learning Platform.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework_simplejwt.views import TokenVerifyView
import os

# Conditional import for API documentation
try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
    HAS_SPECTACULAR = True
except ImportError:
    HAS_SPECTACULAR = False

# Import page URLs from each app
from apps.users.urls import auth_urlpatterns, page_urlpatterns as users_page_urlpatterns
from apps.curriculum.urls import page_urlpatterns as curriculum_page_urlpatterns

# Frontend directory path
FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'public')

def serve_frontend(request, path='index.html'):
    """Serve frontend files from public directory."""
    from django.http import FileResponse, Http404
    import mimetypes
    
    file_path = os.path.join(FRONTEND_DIR, path)
    
    if os.path.isfile(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    raise Http404("File not found")

def serve_assets(request, path):
    """Serve assets files."""
    from django.http import FileResponse, Http404
    import mimetypes
    
    assets_dir = os.path.join(settings.BASE_DIR.parent, 'assets')
    file_path = os.path.join(assets_dir, path)
    
    if os.path.isfile(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    raise Http404("File not found")

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # USER PAGES (Django Templates) - Auth, profile, dashboard pages
    # Namespace: 'users' - Usage: {% url 'users:login' %}
    # =========================================================================
    path('', include((users_page_urlpatterns, 'users'), namespace='users')),
    
    # =========================================================================
    # CURRICULUM PAGES (Django Templates) - Lessons, pronunciation pages
    # Namespace: 'curriculum' - Usage: {% url 'curriculum:pronunciation-library' %}
    # =========================================================================
    path('', include((curriculum_page_urlpatterns, 'curriculum'), namespace='curriculum')),
    
    # =========================================================================
    # API v1 - Authentication (includes token, register, logout, password-reset)
    # =========================================================================
    path('api/v1/auth/', include(auth_urlpatterns)),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API v1 - Apps
    path('api/v1/users/', include('apps.users.urls')),  # API URLs without namespace
    path('api/v1/', include('apps.curriculum.urls', namespace='curriculum-api')),
    path('api/v1/', include('apps.study.urls', namespace='study')),
    
    # Frontend - Serve assets
    re_path(r'^assets/(?P<path>.*)$', serve_assets, name='serve_assets'),
    
    # Frontend - Serve public pages (static HTML for legacy/testing)
    re_path(r'^public/(?P<path>.*)$', serve_frontend, name='serve_public'),
]

# API Documentation (only if drf-spectacular is installed)
if HAS_SPECTACULAR:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Admin site customization
admin.site.site_header = 'English Learning Platform'
admin.site.site_title = 'English Learning Admin'
admin.site.index_title = 'Quản trị hệ thống'
