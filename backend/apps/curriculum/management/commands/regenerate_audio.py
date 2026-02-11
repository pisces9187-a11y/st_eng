"""
Script: Tạo lại TTS audio cho tất cả phonemes với Edge TTS
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.curriculum.models import Phoneme
from apps.curriculum.services.audio_service import PhonemeAudioService
from django.db import transaction


def regenerate_all_phoneme_audio(force_regenerate=False):
    """
    Tạo lại audio cho tất cả phonemes
    
    Args:
        force_regenerate: Nếu True, tạo lại cả những phonemes đã có audio
    """
    print("="*70)
    print("🔊 TẠO LẠI AUDIO CHO TẤT CẢ PHONEMES")
    print("="*70)
    
    audio_service = PhonemeAudioService()
    
    # Get all phonemes
    phonemes = Phoneme.objects.all().select_related('category')
    total = phonemes.count()
    
    print(f"\n📊 Tổng số phonemes: {total}")
    
    # Get phonemes without audio
    missing = audio_service.get_missing_audio_phonemes()
    
    if force_regenerate:
        print(f"   ⚠️  Force mode: Sẽ tạo lại TẤT CẢ {total} phonemes")
        to_generate = list(phonemes)
    else:
        print(f"   📋 Phonemes chưa có audio: {len(missing)}")
        if not missing:
            print("\n✅ Tất cả phonemes đã có audio!")
            
            # Ask if want to regenerate
            response = input("\n   Có muốn tạo lại TẤT CẢ? (y/N): ").strip().lower()
            if response == 'y':
                to_generate = list(phonemes)
                print(f"\n   ⚠️  Sẽ tạo lại {len(to_generate)} phonemes...")
            else:
                print("\n   ℹ️  Không tạo gì. Thoát.")
                return
        else:
            to_generate = missing
    
    # Group by category for better organization
    from collections import defaultdict
    by_category = defaultdict(list)
    
    for p in to_generate:
        category = p.category.category_type if p.category else 'Unknown'
        by_category[category].append(p)
    
    print(f"\n📋 Danh sách phonemes sẽ tạo:")
    for category, phoneme_list in by_category.items():
        ipa_symbols = ", ".join([f"/{p.ipa_symbol}/" for p in phoneme_list[:10]])
        if len(phoneme_list) > 10:
            ipa_symbols += f" ... (+{len(phoneme_list)-10})"
        print(f"   - {category}: {len(phoneme_list)} phonemes")
        print(f"     {ipa_symbols}")
    
    # Confirm
    if len(to_generate) > 5:
        response = input(f"\n❓ Bắt đầu tạo {len(to_generate)} phonemes? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Hủy bỏ.")
            return
    
    # Generate audio
    print(f"\n{'='*70}")
    print(f"🎯 BẮT ĐẦU TẠO AUDIO")
    print(f"{'='*70}\n")
    
    success_count = 0
    failed_count = 0
    failed_list = []
    
    for i, phoneme in enumerate(to_generate, 1):
        category = phoneme.category.category_type if phoneme.category else 'Unknown'
        
        try:
            print(f"[{i}/{len(to_generate)}] 📝 Tạo audio cho /{phoneme.ipa_symbol}/ ({category})...")
            
            # Try to get/generate audio
            audio = audio_service.get_audio_for_phoneme(
                phoneme=phoneme,
                auto_generate=True,
                use_cache=False  # Force regenerate
            )
            
            if audio:
                file_info = ""
                if audio.audio_file:
                    file_size = os.path.getsize(audio.audio_file.path)
                    file_info = f" ({file_size:,} bytes)"
                
                print(f"   ✅ OK - Source: {audio.source_type}{file_info}")
                success_count += 1
            else:
                print(f"   ❌ FAILED - Không tạo được audio")
                failed_count += 1
                failed_list.append((phoneme.ipa_symbol, "No audio returned"))
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)[:50]}")
            failed_count += 1
            failed_list.append((phoneme.ipa_symbol, str(e)[:50]))
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 KẾT QUẢ")
    print(f"{'='*70}")
    
    print(f"\n✅ Thành công: {success_count}/{len(to_generate)} phonemes")
    
    if failed_count > 0:
        print(f"❌ Thất bại: {failed_count} phonemes")
        print(f"\n   Danh sách thất bại:")
        for ipa, error in failed_list:
            print(f"   - /{ipa}/: {error}")
    
    # Final status
    print(f"\n{'='*70}")
    
    if failed_count == 0:
        print("🎉 HOÀN THÀNH! Tất cả audio đã được tạo thành công!")
    else:
        print("⚠️  Hoàn thành với một số lỗi. Xem danh sách trên.")
    
    print(f"{'='*70}\n")
    
    # Get updated report
    print("\n📊 BÁO CÁO SAU KHI TẠO:")
    report = audio_service.get_audio_quality_report()
    
    print(f"   Total phonemes: {report['total_phonemes']}")
    print(f"   Phonemes with audio: {report['phonemes_with_audio']}")
    print(f"   Coverage: {report['coverage_percent']}%")
    
    print(f"\n   Audio sources:")
    print(f"   - Native: {report['native_audio_count']}")
    print(f"   - TTS: {report['tts_audio_count']}")
    print(f"   - Generated: {report['generated_audio_count']}")
    
    print(f"\n{'='*70}\n")


def clear_tts_cache():
    """Xóa cache TTS"""
    print("="*70)
    print("🗑️  XÓA CACHE TTS")
    print("="*70)
    
    cache_dir = Path(__file__).parent / 'backend' / 'media' / 'tts_audio'
    
    if not cache_dir.exists():
        print(f"\n⚠️  Thư mục không tồn tại: {cache_dir}")
        return
    
    # Count files
    mp3_files = list(cache_dir.glob('*.mp3'))
    
    if not mp3_files:
        print(f"\n✅ Không có file cache nào")
        return
    
    print(f"\n📁 Tìm thấy {len(mp3_files)} files trong {cache_dir}")
    
    # Show some files
    print(f"\n   Ví dụ:")
    for f in mp3_files[:5]:
        size = f.stat().st_size
        print(f"   - {f.name} ({size:,} bytes)")
    if len(mp3_files) > 5:
        print(f"   ... và {len(mp3_files)-5} files khác")
    
    # Confirm
    response = input(f"\n❓ Xóa tất cả {len(mp3_files)} files? (y/N): ").strip().lower()
    
    if response == 'y':
        deleted = 0
        for f in mp3_files:
            try:
                f.unlink()
                deleted += 1
            except Exception as e:
                print(f"   ❌ Lỗi xóa {f.name}: {e}")
        
        print(f"\n✅ Đã xóa {deleted}/{len(mp3_files)} files")
    else:
        print("\n❌ Hủy bỏ.")


def main():
    """Main menu"""
    print("\n" + "="*70)
    print("🎯 EDGE TTS AUDIO GENERATOR")
    print("="*70)
    
    print("\n📋 Chọn hành động:")
    print("   1. Tạo audio cho phonemes chưa có")
    print("   2. Tạo LẠI audio cho TẤT CẢ phonemes")
    print("   3. Xóa cache TTS")
    print("   4. Thoát")
    
    choice = input("\n👉 Chọn (1-4): ").strip()
    
    if choice == '1':
        regenerate_all_phoneme_audio(force_regenerate=False)
    elif choice == '2':
        regenerate_all_phoneme_audio(force_regenerate=True)
    elif choice == '3':
        clear_tts_cache()
    elif choice == '4':
        print("\n👋 Tạm biệt!")
    else:
        print("\n❌ Lựa chọn không hợp lệ")


if __name__ == "__main__":
    main()
