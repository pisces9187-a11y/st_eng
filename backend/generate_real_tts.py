#!/usr/bin/env python
"""
Force generate all phonemes with REAL Edge TTS
"""
import os
import sys
import subprocess

# Đặt environment TRƯỚC khi Django setup
os.environ['MOCK_TTS'] = 'false'
os.environ.pop('DJANGO_SETTINGS_MODULE', None)  # Force reload

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.curriculum.models import Phoneme, AudioSource
from apps.curriculum.services.tts_service import TTSService
from apps.curriculum.tasks import generate_audio_batch
import asyncio

print("=" * 70)
print("REAL EDGE TTS GENERATION (Not Mock)")
print(f"MOCK_TTS environment: {os.environ.get('MOCK_TTS')}")
print("=" * 70)

# Get all phoneme IDs
phoneme_ids = list(Phoneme.objects.values_list('id', flat=True).order_by('id'))
print(f"\nGenerating audio for {len(phoneme_ids)} phonemes...")

# Generate using Celery task
try:
    result = generate_audio_batch(phoneme_ids, 'en-US-AriaNeural')
    print(f"\n✓ Batch generation queued")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\nComplete!")
