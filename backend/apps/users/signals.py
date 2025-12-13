"""
User signals for auto-creating profile and settings.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfile, UserSettings


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """Auto-create UserSettings when User is created."""
    if created:
        UserSettings.objects.create(user=instance)
