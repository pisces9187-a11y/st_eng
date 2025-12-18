#!/usr/bin/env python
"""Debug audio file issues"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from apps.curriculum.models import Phoneme, AudioSource
from django.conf import settings

print("\n" + "="*70)
print("AUDIO FILE DEBUG")
print("="*70)

# Get first phoneme with audio
phoneme = Phoneme.objects.filter(audio_sources__isnull=False).first()
if not phoneme:
    print("No phoneme with audio found!")
    exit(1)

print(f"\nPhoneme: {phoneme.ipa_symbol}")

# Get its audio sources
audios = phoneme.audio_sources.all()
print(f"Audio sources count: {audios.count()}")

for audio in audios[:3]:  # Show first 3
    print(f"\n  Audio ID: {audio.id}")
    print(f"  Voice: {audio.voice_id}")
    print(f"  Source type: {audio.source_type}")
    print(f"  Audio file field: {audio.audio_file}")
    print(f"  Audio file name: {audio.audio_file.name if audio.audio_file else 'None'}")
    print(f"  Audio file URL: {audio.audio_file.url if audio.audio_file else 'None'}")
    
    # Check if file exists
    if audio.audio_file:
        file_path = audio.audio_file.path
        exists = os.path.exists(file_path)
        print(f"  File exists: {exists}")
        if exists:
            size = os.path.getsize(file_path)
            print(f"  File size: {size} bytes")
        else:
            print(f"  File path: {file_path}")

# Test API endpoint
print(f"\n\nTesting API Endpoint:")
from apps.curriculum.services.audio_service import PhonemeAudioService

service = PhonemeAudioService()
url = service.get_audio_url(phoneme)
print(f"  API returned URL: {url}")

if url:
    print(f"  URL is valid: {url}")
else:
    print(f"  ERROR: API returned None")
    
    # Debug why
    audio = service.get_audio_for_phoneme(phoneme)
    print(f"  Audio object: {audio}")
    if audio:
        print(f"    Audio file field: {audio.audio_file}")
        print(f"    get_url() result: {audio.get_url()}")

print("\n" + "="*70 + "\n")
