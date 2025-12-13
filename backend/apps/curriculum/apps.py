"""
Curriculum app configuration.
"""

from django.apps import AppConfig


class CurriculumConfig(AppConfig):
    """Configuration for Curriculum app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.curriculum'
    verbose_name = 'Curriculum Management'
