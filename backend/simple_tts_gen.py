#!/usr/bin/env python
"""
Simple offline TTS generation using pyttsx3
"""
import os
import sys
import django

os.environ['MOCK_TTS'] = 'false'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.curriculum.models import Phoneme, AudioSource
import pyttsx3
from pathlib import Path

print("=" * 70)
print("GENERATING AUDIO WITH pyttsx3")
print("=" * 70)

# Initialize pyttsx3 once
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Get all phonemes
phonemes = Phoneme.objects.all().order_by('id')
count = 0
failed = 0

for phoneme in phonemes:
    try:
        # Skip if already has audio
        if AudioSource.objects.filter(phoneme=phoneme).exists():
            print(f"[SKIP] ID:{phoneme.id} - audio exists")
            continue
        
        text = phoneme.vietnamese_approx or phoneme.ipa_symbol
        voice = 'en-US-AriaNeural'
        
        # Create output path
        audio_dir = Path('media/phonemes/audio/2025/12/15')
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"phoneme_{phoneme.id}_{voice.replace('-', '_')}.mp3"
        output_path = str(audio_dir / filename)
        
        # Generate
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            count += 1
            print(f"[OK] ID:{phoneme.id} -> {filename} ({size} bytes)")
            
            # Create/update AudioSource record
            relative_path = f"phonemes/audio/2025/12/15/{filename}"
            AudioSource.objects.update_or_create(
                phoneme=phoneme,
                defaults={
                    'audio_file': relative_path,
                    'voice_id': voice,
                    'source_type': 'tts',
                    'language': 'en-US'
                }
            )
        else:
            failed += 1
            print(f"[ERROR] ID:{phoneme.id} - file not created")
    
    except Exception as e:
        failed += 1
        print(f"[ERROR] ID:{phoneme.id} - {str(e)[:50]}")

engine.stop()
print("\n" + "=" * 70)
print(f"Complete! Generated: {count}, Failed: {failed}")
print("=" * 70)
