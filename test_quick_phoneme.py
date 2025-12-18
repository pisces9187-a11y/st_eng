"""
Quick Test: Kiểm tra nhanh Edge TTS cho 1 phoneme
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.curriculum.models import Phoneme
from apps.curriculum.services.audio_service import PhonemeAudioService

print("🎯 Quick Test: Tạo audio cho 1 phoneme IPA\n")

# Get first phoneme
try:
    phoneme = Phoneme.objects.first()
    
    if not phoneme:
        print("❌ Không tìm thấy phoneme nào trong database!")
        sys.exit(1)
    
    print(f"📝 Phoneme: /{phoneme.ipa_symbol}/")
    if phoneme.category:
        print(f"   Category: {phoneme.category.category_type}")
    print()
    
    # Initialize service
    audio_service = PhonemeAudioService()
    
    # Try to get audio (with auto-generation)
    print("🔊 Đang lấy/tạo audio...")
    audio = audio_service.get_audio_for_phoneme(
        phoneme=phoneme,
        auto_generate=True
    )
    
    if audio:
        print(f"✅ Thành công!")
        print(f"   Source type: {audio.source_type}")
        print(f"   Voice ID: {audio.voice_id}")
        
        if audio.audio_file:
            print(f"   File: {audio.audio_file.name}")
            if os.path.exists(audio.audio_file.path):
                file_size = os.path.getsize(audio.audio_file.path)
                print(f"   Size: {file_size:,} bytes")
            print(f"   URL: {audio.get_url()}")
    else:
        print("❌ Không thể tạo audio!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
