#!/usr/bin/env python
"""Test MOCK_TTS_MODE functionality"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Test MOCK_TTS_MODE
from apps.curriculum.services.tts_service import MOCK_TTS_MODE
from apps.curriculum.models import Phoneme
from apps.curriculum.tasks import generate_phoneme_audio

print(f"MOCK_TTS environment variable: {os.environ.get('MOCK_TTS')}")
print(f"MOCK_TTS_MODE enabled: {MOCK_TTS_MODE}")

# Get first phoneme
p = Phoneme.objects.first()
print(f"\nTesting with phoneme: {p.ipa_symbol}")
print(f"Phoneme ID: {p.id}")

# Try to generate TTS
try:
    result = generate_phoneme_audio(p.id, 'en-US-AriaNeural')
    print(f"\n✅ Result: {result}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
