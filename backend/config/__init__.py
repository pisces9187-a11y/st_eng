"""
Django configuration initialization.
Import Celery app to ensure it's loaded when Django starts.
"""

# Import celery app
from .celery import app as celery_app

__all__ = ('celery_app',)
