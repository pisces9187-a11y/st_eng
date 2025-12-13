"""
Study app configuration.
"""

from django.apps import AppConfig


class StudyConfig(AppConfig):
    """Configuration for Study app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.study'
    verbose_name = 'Study & Progress Tracking'
