#!/usr/bin/env python
"""
Import pre-collected audio files into database
Maps IPA symbols to audio files and creates AudioSource records
"""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.curriculum.models import Phoneme, AudioSource

# Mapping của IPA symbol tới file audio
AUDIO_FILES = {
    'æ': 'media/phonemes/audio/æ.mp3',
    'aɪ': 'media/phonemes/audio/aɪ.mp3',
    'aʊ': 'media/phonemes/audio/aʊ.mp3',
    'ɑː': 'media/phonemes/audio/ɑː.mp3',
}

print("=" * 70)
print("IMPORTING AUDIO FILES INTO DATABASE")
print("=" * 70)

success = 0
failed = 0

for ipa_symbol, file_path in AUDIO_FILES.items():
    try:
        # Check file exists
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"[SKIP] {ipa_symbol}: File not found - {file_path}")
            failed += 1
            continue
        
        # Get phoneme by IPA symbol
        phoneme = Phoneme.objects.get(ipa_symbol=ipa_symbol)
        
        # Get file size
        file_size = full_path.stat().st_size
        
        # Create relative path for Django FileField
        relative_path = file_path  # Already relative from MEDIA_ROOT
        
        # Create or update AudioSource
        audio_source, created = AudioSource.objects.update_or_create(
            phoneme=phoneme,
            defaults={
                'audio_file': relative_path,
                'voice_id': 'en-US-AriaNeural',
                'source_type': 'native',  # Mark as manually imported
                'language': 'en-US'
            }
        )
        
        action = "Created" if created else "Updated"
        print(f"[OK] {ipa_symbol}: {action} AudioSource")
        print(f"     File: {file_path} ({file_size} bytes)")
        success += 1
        
    except Phoneme.DoesNotExist:
        print(f"[ERROR] {ipa_symbol}: Phoneme not found in database")
        failed += 1
    except Exception as e:
        print(f"[ERROR] {ipa_symbol}: {str(e)[:60]}")
        failed += 1

print("\n" + "=" * 70)
print(f"Complete! Success: {success}, Failed: {failed}")
print("=" * 70)
