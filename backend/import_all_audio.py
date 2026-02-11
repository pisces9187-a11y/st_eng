#!/usr/bin/env python
"""
Auto-import all IPA audio files from media/phonemes/audio/ to database
"""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.curriculum.models import Phoneme, AudioSource

# Find all MP3 files in audio directory
AUDIO_DIR = Path('media/phonemes/audio')
audio_files = sorted(AUDIO_DIR.glob('*.mp3'))

print("=" * 70)
print("AUTO-IMPORTING ALL IPA AUDIO FILES")
print("=" * 70)
print(f"\nFound {len(audio_files)} audio files\n")

success = 0
failed = 0
skipped = 0

for audio_file in audio_files:
    filename = audio_file.name
    
    # Skip phoneme_* files (generated ones)
    if filename.startswith('phoneme_'):
        skipped += 1
        continue
    
    # Extract IPA symbol from filename (without .mp3)
    ipa_symbol = filename[:-4]  # Remove .mp3
    
    try:
        # Get phoneme by IPA symbol
        phoneme = Phoneme.objects.get(ipa_symbol=ipa_symbol)
        
        # Get file size
        file_size = audio_file.stat().st_size
        
        # Create relative path
        relative_path = f"phonemes/audio/{filename}"
        
        # Create or update AudioSource
        audio_source, created = AudioSource.objects.update_or_create(
            phoneme=phoneme,
            defaults={
                'audio_file': relative_path,
                'voice_id': 'native-speaker',
                'source_type': 'native',
                'language': 'en-US'
            }
        )
        
        action = "Created" if created else "Updated"
        print(f"[OK] /{ipa_symbol}/ -> {filename} ({file_size} bytes) - {action}")
        success += 1
        
    except Phoneme.DoesNotExist:
        print(f"[SKIP] /{ipa_symbol}/ -> Phoneme not found")
        skipped += 1
    except Exception as e:
        print(f"[ERROR] /{ipa_symbol}/ -> {str(e)[:50]}")
        failed += 1

print("\n" + "=" * 70)
print(f"Results: Success={success}, Failed={failed}, Skipped={skipped}")
print("=" * 70)
