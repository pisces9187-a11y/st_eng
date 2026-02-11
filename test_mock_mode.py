"""
Test với Mock Mode - Không cần internet
"""

import os
import sys
import django

# Enable Mock mode
os.environ['MOCK_TTS'] = 'true'

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.curriculum.models import Phoneme
from apps.curriculum.services.audio_service import PhonemeAudioService
from apps.curriculum.services.edge_tts_service import get_tts_service

print("="*70)
print("🧪 TEST VỚI MOCK MODE (Offline Testing)")
print("="*70)
print()

# Test 1: Basic mock generation
print("TEST 1: Tạo audio mock cho từ đơn giản")
print("-" * 70)
tts = get_tts_service()

audio_path = tts.generate_word_pronunciation_sync(
    word="hello",
    accent="us",
    repeat=1
)

if os.path.exists(audio_path):
    size = os.path.getsize(audio_path)
    print(f"✅ Mock audio created: {audio_path}")
    print(f"   File size: {size} bytes")
else:
    print(f"❌ Failed to create mock audio")

print()

# Test 2: Phoneme với ký tự đặc biệt
print("TEST 2: Tạo audio cho phoneme với ký tự đặc biệt")
print("-" * 70)

test_phonemes = ["æ", "ɪ", "ʌ", "ŋ", "ð", "θ"]

for phoneme_symbol in test_phonemes:
    try:
        audio_path = tts.generate_word_pronunciation_sync(
            word=phoneme_symbol,
            accent="us",
            repeat=2
        )
        
        if os.path.exists(audio_path):
            print(f"✅ /{phoneme_symbol}/ -> {os.path.basename(audio_path)}")
        else:
            print(f"❌ /{phoneme_symbol}/ -> Failed")
            
    except Exception as e:
        print(f"❌ /{phoneme_symbol}/ -> Error: {e}")

print()

# Test 3: Auto-generation với phoneme từ database
print("TEST 3: Auto-generation cho phoneme từ database")
print("-" * 70)

try:
    audio_service = PhonemeAudioService()
    
    # Get phoneme without audio
    missing = audio_service.get_missing_audio_phonemes()
    
    if missing:
        phoneme = missing[0]
        print(f"Testing với phoneme: /{phoneme.ipa_symbol}/")
        
        audio = audio_service.get_audio_for_phoneme(
            phoneme=phoneme,
            auto_generate=True,
            use_cache=False
        )
        
        if audio:
            print(f"✅ Audio generated successfully!")
            print(f"   Source type: {audio.source_type}")
            print(f"   Voice ID: {audio.voice_id}")
            if audio.audio_file:
                print(f"   File: {audio.audio_file.name}")
        else:
            print(f"❌ Failed to generate audio")
    else:
        print("ℹ️  Tất cả phonemes đã có audio, test với phoneme đầu tiên...")
        phoneme = Phoneme.objects.first()
        print(f"Testing với: /{phoneme.ipa_symbol}/")
        
        audio = audio_service.get_audio_for_phoneme(phoneme)
        if audio:
            print(f"✅ Audio retrieved: {audio.source_type}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Sentence generation
print("TEST 4: Tạo audio cho câu")
print("-" * 70)

try:
    audio_path = audio_service.generate_sentence_audio(
        text="The weather is beautiful today.",
        voice_key="us_female_clear",
        speed_level="beginner"
    )
    
    if audio_path and os.path.exists(audio_path):
        print(f"✅ Sentence audio created: {os.path.basename(audio_path)}")
        print(f"   Size: {os.path.getsize(audio_path)} bytes")
    else:
        print(f"❌ Failed to create sentence audio")
        
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 5: Flashcard audio
print("TEST 5: Tạo flashcard audio")
print("-" * 70)

try:
    audio_dict = audio_service.generate_flashcard_audio(
        word="beautiful",
        definition="pleasing to the eye",
        example="She has a beautiful smile.",
        accent="us"
    )
    
    if audio_dict:
        print(f"✅ Flashcard audio created:")
        for key, path in audio_dict.items():
            if path and os.path.exists(path):
                print(f"   - {key}: {os.path.basename(path)}")
            else:
                print(f"   - {key}: Failed")
    else:
        print(f"❌ Failed to create flashcard audio")
        
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("="*70)
print("✅ MOCK MODE TEST COMPLETE")
print("="*70)
print()
print("💡 Lưu ý: Đây là mock audio (sine wave tone)")
print("   Để test với Edge TTS thật, set MOCK_TTS=false")
