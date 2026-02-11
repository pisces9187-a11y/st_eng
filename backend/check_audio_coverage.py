#!/usr/bin/env python
"""Check phoneme audio coverage"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from apps.curriculum.models import Phoneme, AudioSource

total = Phoneme.objects.count()
with_audio = Phoneme.objects.filter(audio_sources__isnull=False).distinct().count()
without_audio = total - with_audio
audio_count = AudioSource.objects.count()

print(f"\n📊 Phoneme Audio Coverage:")
print(f"  Total phonemes: {total}")
print(f"  With audio: {with_audio} ({with_audio*100//total}%)")
print(f"  Without audio: {without_audio}")
print(f"  Total AudioSource records: {audio_count}\n")
