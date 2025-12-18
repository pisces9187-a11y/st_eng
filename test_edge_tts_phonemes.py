"""
Test Script: Kiểm tra tạo audio cho các âm IPA với Edge TTS
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
from apps.curriculum.services.edge_tts_service import get_tts_service


def test_edge_tts_basic():
    """Test 1: Kiểm tra Edge TTS service cơ bản"""
    print("\n" + "="*70)
    print("TEST 1: Kiểm tra Edge TTS Service cơ bản")
    print("="*70)
    
    try:
        tts = get_tts_service()
        print("✅ EnglishTTSService initialized successfully")
        print(f"   Output directory: {tts.output_dir}")
        print(f"   Default voice: {tts.default_voice}")
        print(f"   Default speed: {tts.default_speed_level}")
        
        # Test tạo audio đơn giản
        print("\n📝 Testing word pronunciation generation...")
        audio_path = tts.generate_word_pronunciation_sync(
            word="test",
            accent="us",
            repeat=1,
            speed_level="beginner"
        )
        
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"✅ Audio generated: {audio_path}")
            print(f"   File size: {file_size} bytes")
        else:
            print(f"❌ Audio file not found: {audio_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phoneme_list():
    """Test 2: Kiểm tra danh sách phonemes trong database"""
    print("\n" + "="*70)
    print("TEST 2: Kiểm tra danh sách Phonemes")
    print("="*70)
    
    try:
        phonemes = Phoneme.objects.all().select_related('category')
        total = phonemes.count()
        
        print(f"\n📊 Tổng số phonemes: {total}")
        
        if total == 0:
            print("⚠️  Không có phoneme nào trong database!")
            return False
        
        # Group by category
        from django.db.models import Count
        by_category = Phoneme.objects.values('category__category_type').annotate(
            count=Count('id')
        )
        
        print("\n📋 Phân loại:")
        for item in by_category:
            cat_type = item['category__category_type'] or 'Unknown'
            count = item['count']
            print(f"   - {cat_type}: {count} phonemes")
        
        # Show first 10 phonemes
        print("\n📝 10 phonemes đầu tiên:")
        for phoneme in phonemes[:10]:
            category = phoneme.category.category_type if phoneme.category else 'Unknown'
            print(f"   - /{phoneme.ipa_symbol}/ ({category})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phoneme_audio_status():
    """Test 3: Kiểm tra trạng thái audio của phonemes"""
    print("\n" + "="*70)
    print("TEST 3: Kiểm tra trạng thái Audio của Phonemes")
    print("="*70)
    
    try:
        audio_service = PhonemeAudioService()
        
        # Get quality report
        print("\n📊 Audio Quality Report:")
        report = audio_service.get_audio_quality_report()
        
        print(f"   Total phonemes: {report['total_phonemes']}")
        print(f"   Phonemes with audio: {report['phonemes_with_audio']}")
        print(f"   Phonemes without audio: {report['phonemes_without_audio']}")
        print(f"   Coverage: {report['coverage_percent']}%")
        print(f"   Average quality score: {report['avg_quality_score']}")
        
        print(f"\n   Audio sources:")
        print(f"   - Native: {report['native_audio_count']}")
        print(f"   - TTS: {report['tts_audio_count']}")
        print(f"   - Generated: {report['generated_audio_count']}")
        
        print(f"\n   By category:")
        for cat_type, data in report['by_category'].items():
            print(f"   - {cat_type}: {data['with_audio']}/{data['total']} ({data['coverage']}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_generation():
    """Test 4: Kiểm tra auto-generation cho phonemes"""
    print("\n" + "="*70)
    print("TEST 4: Kiểm tra Auto-Generation cho Phonemes")
    print("="*70)
    
    try:
        audio_service = PhonemeAudioService()
        
        # Get phonemes without audio
        missing = audio_service.get_missing_audio_phonemes()
        
        if not missing:
            print("\n✅ Tất cả phonemes đã có audio!")
            # Test với phoneme đầu tiên
            phoneme = Phoneme.objects.first()
        else:
            print(f"\n📋 Có {len(missing)} phonemes chưa có audio")
            print(f"   Sẽ test với phoneme đầu tiên chưa có audio...")
            phoneme = missing[0]
        
        print(f"\n🎯 Test phoneme: /{phoneme.ipa_symbol}/")
        print(f"   Category: {phoneme.category.category_type if phoneme.category else 'Unknown'}")
        
        # Try to get audio with auto-generation
        print("\n📝 Đang lấy/tạo audio (auto_generate=True)...")
        audio = audio_service.get_audio_for_phoneme(
            phoneme=phoneme,
            auto_generate=True,
            use_cache=False  # Force generation để test
        )
        
        if audio:
            print(f"✅ Audio obtained successfully!")
            print(f"   Source type: {audio.source_type}")
            print(f"   Voice ID: {audio.voice_id}")
            print(f"   File: {audio.audio_file.name if audio.audio_file else 'N/A'}")
            
            if audio.audio_file:
                file_path = audio.audio_file.path
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   File size: {file_size} bytes")
                    
                    # Get URL
                    url = audio.get_url()
                    print(f"   URL: {url}")
            
            return True
        else:
            print(f"❌ Failed to get/generate audio")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bulk_generation():
    """Test 5: Kiểm tra bulk generation"""
    print("\n" + "="*70)
    print("TEST 5: Kiểm tra Bulk Generation (tạo 3 phonemes)")
    print("="*70)
    
    try:
        audio_service = PhonemeAudioService()
        
        # Get phonemes without audio (max 3 để test)
        missing = audio_service.get_missing_audio_phonemes()[:3]
        
        if not missing:
            print("\n✅ Tất cả phonemes đã có audio!")
            print("   Sử dụng 3 phonemes đầu tiên để test...")
            missing = list(Phoneme.objects.all()[:3])
        
        print(f"\n📋 Sẽ tạo audio cho {len(missing)} phonemes:")
        for p in missing:
            print(f"   - /{p.ipa_symbol}/")
        
        print("\n📝 Đang tạo audio bulk...")
        results = audio_service.bulk_generate_phoneme_audio(
            phonemes=missing,
            voice_key="us_female_clear"
        )
        
        print(f"\n✅ Hoàn thành: {len(results)}/{len(missing)} phonemes")
        
        for phoneme_id, audio in results.items():
            phoneme = Phoneme.objects.get(id=phoneme_id)
            print(f"   - /{phoneme.ipa_symbol}/: {audio.source_type}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_voice_comparison():
    """Test 6: So sánh các giọng nói khác nhau"""
    print("\n" + "="*70)
    print("TEST 6: So sánh các giọng nói (US vs GB)")
    print("="*70)
    
    try:
        tts = get_tts_service()
        test_word = "hello"
        
        voices_to_test = [
            ("us_female_clear", "US Female"),
            ("us_male_standard", "US Male"),
            ("gb_female", "GB Female"),
            ("gb_male", "GB Male"),
        ]
        
        print(f"\n📝 Tạo audio cho từ '{test_word}' với các giọng khác nhau:\n")
        
        for voice_key, description in voices_to_test:
            try:
                audio_path = tts.generate_word_pronunciation_sync(
                    word=test_word,
                    accent="us" if "us_" in voice_key else "gb",
                    repeat=1,
                    speed_level="intermediate"
                )
                
                if os.path.exists(audio_path):
                    file_size = os.path.getsize(audio_path)
                    print(f"   ✅ {description}: {file_size} bytes")
                else:
                    print(f"   ❌ {description}: File not found")
                    
            except Exception as e:
                print(f"   ❌ {description}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("🎯 EDGE TTS INTEGRATION TEST - PHONEME AUDIO GENERATION")
    print("="*70)
    
    tests = [
        ("Basic Edge TTS", test_edge_tts_basic),
        ("Phoneme List", test_phoneme_list),
        ("Audio Status", test_phoneme_audio_status),
        ("Auto-Generation", test_auto_generation),
        ("Bulk Generation", test_bulk_generation),
        ("Voice Comparison", test_voice_comparison),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Edge TTS integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
