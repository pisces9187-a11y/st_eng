"""
Test Real Edge TTS API - Kiểm tra với các từ đơn giản trước
"""

import os
import sys
import django

# Disable Mock mode - use real Edge TTS
os.environ['MOCK_TTS'] = 'false'

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.curriculum.services.edge_tts_service import get_tts_service
import asyncio

print("="*70)
print("🌐 TEST VỚI EDGE TTS API THỰC")
print("="*70)
print()

tts = get_tts_service()

# Test với các từ đơn giản trước
test_cases = [
    ("hello", "us", "Từ đơn giản tiếng Anh"),
    ("world", "us", "Từ phổ biến"),
    ("test", "gb", "Giọng Anh"),
]

print("TEST 1: Tạo audio cho từ đơn giản")
print("-" * 70)

for word, accent, description in test_cases:
    print(f"\nTesting: {word} ({description})")
    try:
        audio_path = tts.generate_word_pronunciation_sync(
            word=word,
            accent=accent,
            repeat=1,
            speed_level="intermediate"
        )
        
        if os.path.exists(audio_path):
            size = os.path.getsize(audio_path)
            print(f"✅ Success! File: {os.path.basename(audio_path)}")
            print(f"   Size: {size:,} bytes")
        else:
            print(f"❌ File not found: {audio_path}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}...")

print()
print("="*70)

# Test với câu
print("\nTEST 2: Tạo audio cho câu")
print("-" * 70)

try:
    # Thử với câu ngắn
    audio_path = tts.generate_sentence_audio_sync(
        sentence="Hello, how are you?",
        student_level="intermediate",
        voice_type="female",
        accent="us"
    )
    
    if audio_path and os.path.exists(audio_path):
        size = os.path.getsize(audio_path)
        print(f"✅ Sentence audio created!")
        print(f"   File: {os.path.basename(audio_path)}")
        print(f"   Size: {size:,} bytes")
    else:
        print(f"❌ Failed")
        
except Exception as e:
    print(f"❌ Error: {str(e)[:100]}...")

print()

# Test list voices
print("\nTEST 3: Kiểm tra danh sách giọng nói có sẵn")
print("-" * 70)

async def test_list_voices():
    try:
        voices = await tts.list_all_english_voices()
        
        if voices:
            print(f"✅ Found {len(voices)} English voices")
            print("\nMột số giọng phổ biến:")
            
            for v in voices[:10]:
                print(f"   - {v['name']} ({v['locale']}, {v['gender']})")
        else:
            print("❌ No voices found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

try:
    asyncio.run(test_list_voices())
except Exception as e:
    print(f"❌ Cannot list voices: {e}")

print()
print("="*70)
print("✅ TEST COMPLETE")
print("="*70)
print()
print("💡 Lưu ý:")
print("   - Nếu thấy lỗi 'No audio received', kiểm tra kết nối internet")
print("   - Có thể Edge TTS API đang bị rate limit")
print("   - Thử lại sau vài giây hoặc dùng Mock mode để test")
