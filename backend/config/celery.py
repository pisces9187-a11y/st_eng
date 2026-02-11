"""
Celery Configuration for English Study Platform

This module configures Celery for async task processing:
- TTS audio generation
- Batch processing
- Periodic tasks (cache cleanup)

Setup:
    1. Start Redis: redis-server
    2. Start Celery Worker: celery -A config worker -l info
    3. Start Celery Beat: celery -A config beat -l info
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app
app = Celery('english_study')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule (Periodic Tasks)
app.conf.beat_schedule = {
    # Clean expired TTS cache daily at 2 AM
    'clean-expired-audio-cache': {
        'task': 'apps.curriculum.tasks.clean_expired_audio_cache',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Generate missing audio for new phonemes daily at 3 AM
    'generate-missing-audio': {
        'task': 'apps.curriculum.tasks.generate_missing_audio_batch',
        'schedule': crontab(hour=3, minute=0),
    },
    
    # NEW: Clean expired flashcard audio daily at 4 AM
    'clean-expired-flashcard-audio': {
        'task': 'apps.vocabulary.tasks.clean_expired_flashcard_audio',
        'schedule': crontab(hour=4, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')
