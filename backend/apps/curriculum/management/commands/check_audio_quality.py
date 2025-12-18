"""
Kiểm tra Django TTS Service và Mock Mode
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings
from apps.curriculum.services.edge_tts_service import get_tts_service, get_mock_tts_mode


def check_settings():
    """Kiểm tra cài đặt"""
    print("="*70)
    print("🔍 KIỂM TRA CÀI ĐẶT")
    print("="*70)
    
    print(f"\n📋 Django Settings:")
    print(f"   DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    print(f"\n🎤 TTS Settings:")
    mock_mode = get_mock_tts_mode()
    print(f"   MOCK_TTS_MODE (from settings): {getattr(settings, 'MOCK_TTS_MODE', 'NOT SET')}")
    print(f"   MOCK_TTS (from env): {os.environ.get('MOCK_TTS', 'NOT SET')}")
    print(f"   get_mock_tts_mode(): {mock_mode}")
    
    if mock_mode:
        print("\n   ⚠️  CẢNH BÁO: MOCK MODE ĐANG BẬT!")
        print("   -> Đây là lý do tất cả audio đều là beep")
    else:
        print("\n   ✅ Mock mode KHÔNG bật - sẽ dùng Edge TTS thật")
    
    return mock_mode


def test_tts_service():
    """Test TTS Service"""
    print("\n" + "="*70)
    print("🎯 TEST TTS SERVICE")
    print("="*70)
    
    try:
        tts = get_tts_service()
        print(f"\n✅ TTS Service initialized")
        print(f"   Output dir: {tts.output_dir}")
        print(f"   Default voice: {tts.default_voice}")
        print(f"   Default speed: {tts.default_speed_level}")
        
        # Test generation
        print("\n📝 Testing audio generation...")
        audio_path = tts.generate_word_pronunciation_sync(
            word="hello",
            accent="us",
            repeat=1,
            speed_level="intermediate"
        )
        
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"\n✅ Audio generated: {audio_path}")
            print(f"   File size: {file_size:,} bytes")
            
            # Check if mock
            if file_size == 49571:
                print(f"   ⚠️  ĐÂY LÀ MOCK AUDIO (beep sound)!")
                print(f"   -> Size 49571 bytes là mock audio từ pydub")
            elif file_size < 1000:
                print(f"   ⚠️  File quá nhỏ - có thể là file rỗng")
            else:
                print(f"   ✅ File size hợp lý - có thể là Edge TTS thật")
                
        else:
            print(f"❌ File not found: {audio_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("🔧 DJANGO TTS DIAGNOSTIC")
    print("="*70)
    
    # Check settings
    is_mock = check_settings()
    
    # Test service
    test_tts_service()
    
    # Summary
    print("\n" + "="*70)
    print("📊 KẾT LUẬN")
    print("="*70)
    
    if is_mock:
        print("\n❌ Vấn đề: MOCK MODE đang bật")
        print("\n💡 Giải pháp:")
        print("   1. Thêm vào backend/.env:")
        print("      MOCK_TTS=false")
        print("\n   2. Hoặc xóa dòng set MOCK_TTS trong file .bat")
        print("\n   3. Hoặc chạy:")
        print("      $env:MOCK_TTS='false'")
        print("      python test_edge_tts_phonemes.py")
    else:
        print("\n✅ Mock mode không bật")
        print("   Nếu vẫn nghe beep, kiểm tra:")
        print("   1. Kết nối internet")
        print("   2. Version edge-tts: pip show edge-tts")
        print("   3. Log trong Django console")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
