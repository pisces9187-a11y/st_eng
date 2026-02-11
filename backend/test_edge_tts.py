#!/usr/bin/env python
"""
Generate audio using real Edge TTS (not mock mode)
"""
import os
import sys
import django
from django.db import connection
from django.db.utils import OperationalError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.curriculum.models import Phoneme, AudioSource
from apps.curriculum.services.tts_service import TTSService
import asyncio

# Force real TTS, not mock
os.environ['MOCK_TTS'] = 'false'

# Phonemes to generate
phoneme_ids = [45, 46, 47, 48, 49, 50]  # First 6 phonemes for testing

service = TTSService()

def test_edge_tts_sync():
    """Test Edge TTS with real API (sync wrapper)"""
    print("=" * 70)
    print("TESTING EDGE TTS (Real API)")
    print("=" * 70)
    
    for phoneme_id in phoneme_ids:
        try:
            phoneme = Phoneme.objects.get(id=phoneme_id)
            text = phoneme.vietnamese_approx or phoneme.ipa_symbol  # e.g., "i ngan (sit)"
            voice = 'en-US-AriaNeural'
            
            print(f"\nGenerating audio for: {phoneme.ipa_symbol} - {text}")
            
            # Generate with real Edge TTS
            audio_path = asyncio.run(service.generate_audio(text=text, voice=voice, rate='-30%'))
            
            if audio_path and os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"[OK] Generated: {audio_path}")
                print(f"  Size: {file_size} bytes")
            else:
                print(f"[ERROR] Failed to generate")
                
        except Phoneme.DoesNotExist:
            print(f"[ERROR] Phoneme {phoneme_id} not found")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == '__main__':
    test_edge_tts_sync()
