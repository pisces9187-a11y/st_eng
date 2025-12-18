#!/usr/bin/env python
"""Regenerate audio files with proper names"""
import os
import sys
import django
import shutil

os.environ['MOCK_TTS'] = 'true'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from apps.curriculum.models import Phoneme, AudioSource
from django.conf import settings

print("\n" + "="*70)
print("FIX AUDIO FILE NAMES")
print("="*70)

# Delete old audio files
audio_dir = os.path.join(settings.MEDIA_ROOT, 'phonemes', 'audio')
if os.path.exists(audio_dir):
    print(f"\nDeleting old audio directory: {audio_dir}")
    shutil.rmtree(audio_dir)
    print("[OK] Old audio files deleted")

# Delete all AudioSource records
count = AudioSource.objects.count()
AudioSource.objects.all().delete()
print(f"\nDeleted {count} AudioSource records")

# Regenerate with correct file names
print(f"\nRegenerating audio for all phonemes...")
from apps.curriculum.tasks import generate_audio_batch

phoneme_ids = list(Phoneme.objects.values_list('id', flat=True))
result = generate_audio_batch(phoneme_ids, 'en-US-AriaNeural')

print(f"\nResults:")
print(f"  Total: {result['total']}")
print(f"  Successful: {result['successful']}")
print(f"  Failed: {result['failed']}")

# Verify new file names
print(f"\n\nVerifying file names:")
audio = AudioSource.objects.filter(audio_file__isnull=False).first()
if audio:
    print(f"  Sample audio file: {audio.audio_file.name}")
    print(f"  File URL: {audio.audio_file.url}")
    
    # Check if file exists
    if os.path.exists(audio.audio_file.path):
        size = os.path.getsize(audio.audio_file.path)
        print(f"  [OK] File exists ({size} bytes)")
    else:
        print(f"  [ERROR] File not found at: {audio.audio_file.path}")

print("\n" + "="*70 + "\n")
