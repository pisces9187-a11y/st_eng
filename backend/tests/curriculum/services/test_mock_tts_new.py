#!/usr/bin/env python
"""Test script for mock TTS mode"""
import os
import sys
import django

# Set MOCK_TTS environment variable BEFORE django setup
os.environ['MOCK_TTS'] = 'true'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from apps.curriculum.tasks import generate_phoneme_audio
from apps.curriculum.models import Phoneme, AudioSource

print("\n" + "="*60)
print("MOCK TTS MODE TEST")
print("="*60)

# Check current MOCK_TTS setting
from django.conf import settings
print(f"\nMOCK_TTS_MODE setting: {getattr(settings, 'MOCK_TTS_MODE', False)}")

# Try to find a phoneme without audio
phoneme = Phoneme.objects.filter(audio_sources__isnull=True).first()

if phoneme:
    print(f"\nTesting with phoneme: {phoneme.ipa_symbol}")
    print(f"Phoneme ID: {phoneme.id}")
    
    # Delete any existing audio for clean test
    AudioSource.objects.filter(phoneme=phoneme).delete()
    
    # Generate mock audio
    print("\nGenerating mock TTS audio...")
    result = generate_phoneme_audio(phoneme.id, 'en-US-AriaNeural')
    
    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Phoneme ID: {result['phoneme_id']}")
    print(f"  Audio Source ID: {result.get('audio_source_id', 'N/A')}")
    print(f"  Message: {result['message']}")
    
    # Verify audio was created
    audio = AudioSource.objects.filter(phoneme=phoneme).first()
    if audio:
        print(f"\nAudio file created:")
        print(f"  File: {audio.audio_file.name if audio.audio_file else 'N/A'}")
        print(f"  Voice: {audio.voice_id}")
        print(f"  File size: {audio.audio_file.size if audio.audio_file else 'N/A'} bytes")
    
    print("\n✅ Mock TTS test PASSED")
else:
    print("\nNo phonemes without audio found.")
    # Test with first phoneme anyway
    phoneme = Phoneme.objects.first()
    if phoneme:
        print(f"Testing with existing phoneme: {phoneme.ipa_symbol}")
        result = generate_phoneme_audio(phoneme.id, 'en-US-AriaNeural', force_regenerate=True)
        print(f"Result: {result}")

print("\n" + "="*60 + "\n")
