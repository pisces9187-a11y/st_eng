"""
Script: Tạo TTS audio cho phonemes bằng VÍ DỤ TỪ TIẾNG ANH
Giải pháp: Thay vì đọc ký tự IPA, đọc từ tiếng Anh có chứa âm đó
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


# Map phoneme -> example word that clearly demonstrates the sound
PHONEME_EXAMPLES = {
    # Vowels
    '/ɪ/': 'bit',
    '/e/': 'bed',
    '/æ/': 'cat',
    '/ʌ/': 'cup',
    '/ʊ/': 'book',
    '/ɒ/': 'hot',
    '/ə/': 'about',
    '/i:/': 'bee',
    '/iː/': 'see',
    '/uː/': 'too',
    '/ɜː/': 'bird',
    '/ɔː/': 'door',
    '/ɑː/': 'far',
    
    # Diphthongs
    '/eɪ/': 'day',
    '/aɪ/': 'my',
    '/ɔɪ/': 'boy',
    '/aʊ/': 'now',
    '/əʊ/': 'go',
    '/ɪə/': 'here',
    '/eə/': 'hair',
    '/ʊə/': 'tour',
    
    # Consonants
    '/p/': 'pet',
    '/t/': 'ten',
    '/k/': 'cat',
    '/f/': 'fan',
    '/θ/': 'think',
    '/s/': 'see',
    '/ʃ/': 'shoe',
    '/tʃ/': 'church',
    '/h/': 'hat',
    '/b/': 'big',
    '/d/': 'dog',
    '/g/': 'go',
    '/v/': 'very',
    '/ð/': 'this',
    '/z/': 'zoo',
    '/ʒ/': 'measure',
    '/dʒ/': 'jump',
    '/m/': 'man',
    '/n/': 'no',
    '/ŋ/': 'sing',
    '/l/': 'let',
    '/r/': 'red',
    '/w/': 'wet',
    '/j/': 'yes',
}


async def generate_phoneme_with_example(phoneme, tts_service, voice_key="us_female_clear"):
    """
    Tạo audio cho phoneme bằng từ ví dụ
    
    Args:
        phoneme: Phoneme object
        tts_service: TTS service instance
        voice_key: Giọng nói
    
    Returns:
        Đường dẫn file audio
    """
    ipa = f"/{phoneme.ipa_symbol}/"
    
    # Get example word
    example_word = PHONEME_EXAMPLES.get(ipa, phoneme.ipa_symbol)
    
    # If we have an example word, repeat it 3 times
    if example_word != phoneme.ipa_symbol:
        text = f"{example_word} ... {example_word} ... {example_word}"
    else:
        # Fallback: try the IPA symbol itself
        text = f"{phoneme.ipa_symbol} ... {phoneme.ipa_symbol}"
    
    # Generate custom filename
    import hashlib
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    filename = f"phoneme_{phoneme.ipa_symbol}_{voice_key}_{text_hash}"
    
    # Generate audio
    audio_path = await tts_service.generate_speech(
        text=text,
        voice_key=voice_key,
        speed_level="beginner",  # Slow for learning
        filename=filename,
        use_cache=False  # Force regenerate
    )
    
    return audio_path, example_word


async def bulk_generate_with_examples(phonemes, voice_key="us_female_clear"):
    """
    Tạo hàng loạt audio cho phonemes với từ ví dụ
    
    Args:
        phonemes: Danh sách Phoneme objects
        voice_key: Giọng nói
    
    Returns:
        Dict mapping phoneme.id -> (audio_path, example_word)
    """
    tts_service = get_tts_service()
    results = {}
    
    for phoneme in phonemes:
        try:
            audio_path, example_word = await generate_phoneme_with_example(
                phoneme=phoneme,
                tts_service=tts_service,
                voice_key=voice_key
            )
            
            if audio_path and os.path.exists(audio_path):
                results[phoneme.id] = (audio_path, example_word)
                file_size = os.path.getsize(audio_path)
                print(f"   ✅ /{phoneme.ipa_symbol}/ -> \"{example_word}\" -> {os.path.basename(audio_path)} ({file_size:,} bytes)")
            else:
                print(f"   ❌ /{phoneme.ipa_symbol}/ -> File not created")
                
        except Exception as e:
            print(f"   ❌ /{phoneme.ipa_symbol}/ -> Error: {str(e)[:60]}")
    
    return results


def main():
    """Main function"""
    print("="*70)
    print("🔊 TẠO TTS AUDIO CHO PHONEMES (Sử dụng Từ Ví Dụ)")
    print("="*70)
    
    print("\n💡 Phương pháp: Thay vì đọc ký tự IPA, đọc từ tiếng Anh")
    print("   Ví dụ: /ɪ/ -> 'bit', /θ/ -> 'think', /ʃ/ -> 'shoe'")
    
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
    
    # Show examples
    print(f"\n📝 Ví dụ mapping:")
    examples = [
        ('/ɪ/', 'bit'),
        ('/θ/', 'think'),
        ('/ʃ/', 'shoe'),
        ('/ð/', 'this'),
        ('/ʒ/', 'measure'),
        ('/ʊ/', 'book'),
        ('/ə/', 'about'),
    ]
    for ipa, word in examples:
        print(f"   {ipa:6} -> {word}")
    
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
        
        results = asyncio.run(bulk_generate_with_examples(phoneme_list, voice_key="us_female_clear"))
        all_results.update(results)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 KẾT QUẢ")
    print(f"{'='*70}")
    
    success_count = len(all_results)
    failed_count = total - success_count
    
    print(f"\n✅ Thành công: {success_count}/{total} phonemes ({success_count/total*100:.1f}%)")
    if failed_count > 0:
        print(f"❌ Thất bại: {failed_count} phonemes")
    
    if success_count > 0:
        print(f"\n📁 Tất cả audio đã được lưu trong:")
        print(f"   backend/media/tts_audio/")
        
        # Show some examples
        example_files = list(all_results.values())[:5]
        print(f"\n   Ví dụ:")
        for file_path, example_word in example_files:
            basename = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            print(f"   - {basename} (từ: \"{example_word}\", {size:,} bytes)")
    
    print(f"\n{'='*70}")
    
    if failed_count == 0:
        print("🎉 HOÀN THÀNH! Tất cả audio đã được tạo thành công!")
    else:
        print("⚠️  Hoàn thành với một số lỗi.")
    
    print(f"{'='*70}\n")
    
    # Show how to use
    print("\n💡 Cách sử dụng audio:")
    print("   1. Mỗi phoneme được phát âm trong từ thật")
    print("   2. Lặp 3 lần để rõ ràng")
    print("   3. Tốc độ: beginner (chậm 25%)")
    print("   4. Giọng: US Female (AriaNeural)")
    print("   5. Format: 'word ... word ... word'")
    
    print("\n💡 Các phoneme khó đã được map:")
    difficult_ones = [k for k in PHONEME_EXAMPLES.keys() if k in ['/ʃ/', '/θ/', '/ð/', '/ʒ/', '/ʊ/', '/ə/']]
    for ipa in difficult_ones:
        print(f"   {ipa} -> {PHONEME_EXAMPLES[ipa]}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
