#!/usr/bin/env python
"""Verify audio URLs after fix"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from apps.curriculum.models import Phoneme
from apps.curriculum.services.audio_service import PhonemeAudioService

print("\n" + "="*70)
print("AUDIO URL VERIFICATION")
print("="*70)

service = PhonemeAudioService()

# Test first 5 phonemes
phonemes = Phoneme.objects.all()[:5]

for phoneme in phonemes:
    url = service.get_audio_url(phoneme)
    print(f"\nPhoneme: {phoneme.ipa_symbol} (ID: {phoneme.id})")
    print(f"  URL: {url}")
    
    if url:
        # Check file
        audio = service.get_audio_for_phoneme(phoneme)
        if audio and audio.audio_file:
            exists = os.path.exists(audio.audio_file.path)
            print(f"  File exists: {exists}")
            if exists:
                size = os.path.getsize(audio.audio_file.path)
                print(f"  Size: {size} bytes")

print("\n" + "="*70 + "\n")
