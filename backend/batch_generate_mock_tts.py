#!/usr/bin/env python
"""Batch generate mock TTS audio for all phonemes"""
import os
import sys
import django

os.environ['MOCK_TTS'] = 'true'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from apps.curriculum.models import Phoneme
from apps.curriculum.tasks import generate_audio_batch

print("\n" + "="*60)
print("BATCH GENERATE MOCK TTS AUDIO")
print("="*60)

# Get all phoneme IDs
phonemes_without_audio = Phoneme.objects.filter(audio_sources__isnull=True).values_list('id', flat=True)
phoneme_ids = list(phonemes_without_audio)

print(f"\nGenerating audio for {len(phoneme_ids)} phonemes...")
print(f"MOCK_TTS_MODE enabled: {os.getenv('MOCK_TTS') == 'true'}")

if phoneme_ids:
    result = generate_audio_batch(phoneme_ids, 'en-US-AriaNeural')
    print(f"\nResults:")
    print(f"  Total: {result['total']}")
    print(f"  Successful: {result['successful']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Skipped: {result['skipped']}")
    
    # Show summary
    from apps.curriculum.models import AudioSource
    total = Phoneme.objects.count()
    with_audio = Phoneme.objects.filter(audio_sources__isnull=False).distinct().count()
    
    print(f"\nUpdated Coverage:")
    print(f"  Total phonemes: {total}")
    print(f"  With audio: {with_audio} ({with_audio*100//total}%)")
    print(f"  Total AudioSource records: {AudioSource.objects.count()}")
else:
    print("All phonemes already have audio!")

print("\n" + "="*60 + "\n")
