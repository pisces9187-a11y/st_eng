"""
Script: Tạo TTS audio cho phonemes - BẮT BUỘC dùng Edge TTS
"""

import os
import sys
import django
import asyncio

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.curriculum.models import Phoneme
from apps.curriculum.services.edge_tts_service import get_tts_service


async def generate_phoneme_audio_with_tts(phoneme, tts_service, voice_key="us_female_clear", repeat=2):
    """
    Tạo audio cho phoneme với Edge TTS
    
    Args:
        phoneme: Phoneme object
        tts_service: TTS service instance
        voice_key: Giọng nói
        repeat: Số lần lặp (mặc định: 2)
    
    Returns:
        Đường dẫn file audio
    """
    # Tạo audio
    audio_path = await tts_service.generate_word_pronunciation(
        word=phoneme.ipa_symbol,
        accent="us" if "us_" in voice_key else "gb",
        repeat=repeat,
        speed_level="beginner"  # Slow for pronunciation
    )
    
    return audio_path


async def bulk_generate_phonemes(phonemes, voice_key="us_female_clear"):
    """
    Tạo hàng loạt audio cho phonemes
    
    Args:
        phonemes: Danh sách Phoneme objects
        voice_key: Giọng nói
    
    Returns:
        Dict mapping phoneme.id -> audio_path
    """
    tts_service = get_tts_service()
    results = {}
    
    for phoneme in phonemes:
        try:
            audio_path = await generate_phoneme_audio_with_tts(
                phoneme=phoneme,
                tts_service=tts_service,
                voice_key=voice_key
            )
            
            if audio_path and os.path.exists(audio_path):
                results[phoneme.id] = audio_path
                file_size = os.path.getsize(audio_path)
                print(f"   ✅ /{phoneme.ipa_symbol}/ -> {os.path.basename(audio_path)} ({file_size:,} bytes)")
            else:
                print(f"   ❌ /{phoneme.ipa_symbol}/ -> File not created")
                
        except Exception as e:
            print(f"   ❌ /{phoneme.ipa_symbol}/ -> Error: {str(e)[:50]}")
    
    return results


def main():
    """Main function"""
    print("="*70)
    print("🔊 TẠO TTS AUDIO CHO PHONEMES (Edge TTS)")
    print("="*70)
    
    # Get all phonemes
    phonemes = list(Phoneme.objects.all().select_related('category'))
    total = len(phonemes)
    
    print(f"\n📊 Tổng số phonemes: {total}")
    
    # Group by category
    from collections import defaultdict
    by_category = defaultdict(list)
    
    for p in phonemes:
        category = p.category.category_type if p.category else 'Unknown'
        by_category[category].append(p)
    
    print(f"\n📋 Phân loại:")
    for category, phoneme_list in by_category.items():
        print(f"   - {category}: {len(phoneme_list)} phonemes")
    
    # Confirm
    response = input(f"\n❓ Tạo audio cho {total} phonemes? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Hủy bỏ.")
        return
    
    print(f"\n{'='*70}")
    print(f"🎯 BẮT ĐẦU TẠO AUDIO")
    print(f"{'='*70}\n")
    
    # Generate by category
    all_results = {}
    
    for category, phoneme_list in by_category.items():
        print(f"\n📝 Tạo audio cho {category} ({len(phoneme_list)} phonemes):")
        
        results = asyncio.run(bulk_generate_phonemes(phoneme_list, voice_key="us_female_clear"))
        all_results.update(results)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 KẾT QUẢ")
    print(f"{'='*70}")
    
    success_count = len(all_results)
    failed_count = total - success_count
    
    print(f"\n✅ Thành công: {success_count}/{total} phonemes")
    print(f"❌ Thất bại: {failed_count} phonemes")
    
    if success_count > 0:
        print(f"\n📁 Tất cả audio đã được lưu trong:")
        print(f"   backend/media/tts_audio/")
        
        # Show some examples
        example_files = list(all_results.values())[:5]
        print(f"\n   Ví dụ:")
        for file_path in example_files:
            basename = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            print(f"   - {basename} ({size:,} bytes)")
    
    print(f"\n{'='*70}")
    
    if failed_count == 0:
        print("🎉 HOÀN THÀNH! Tất cả audio đã được tạo thành công!")
    else:
        print("⚠️  Hoàn thành với một số lỗi.")
    
    print(f"{'='*70}\n")
    
    # Show how to use
    print("\n💡 Cách sử dụng audio:")
    print("   1. Audio được lưu trong backend/media/tts_audio/")
    print("   2. Format tên file: word_{ipa}_us_2x.mp3")
    print("   3. Mỗi phoneme được lặp 2 lần để rõ ràng")
    print("   4. Tốc độ: beginner (chậm 25%)")
    print("   5. Giọng: US Female (en-US-AriaNeural)")
    
    print("\n💡 Test audio:")
    if all_results:
        first_file = list(all_results.values())[0]
        print(f"   Mở file: {first_file}")
        print(f"   Hoặc dùng: python -m webbrowser {first_file}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
