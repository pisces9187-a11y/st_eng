"""
Test trực tiếp Edge TTS - Không qua Django
"""

import edge_tts
import asyncio
import os

async def test_direct_edge_tts():
    """Test Edge TTS trực tiếp"""
    print("="*70)
    print("🎯 TEST EDGE TTS TRỰC TIẾP (Không qua Django)")
    print("="*70)
    
    test_text = "Hello, this is a test of Edge TTS. Beautiful pronunciation."
    voice = "en-US-AriaNeural"
    output_file = "test_direct_output.mp3"
    
    print(f"\n📝 Text: {test_text}")
    print(f"🎤 Voice: {voice}")
    print(f"📁 Output: {output_file}")
    
    try:
        print("\n⏳ Generating audio...")
        
        # Tạo audio
        communicate = edge_tts.Communicate(text=test_text, voice=voice)
        await communicate.save(output_file)
        
        # Kiểm tra file
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n✅ SUCCESS!")
            print(f"   File: {output_file}")
            print(f"   Size: {file_size:,} bytes")
            
            # Kiểm tra nội dung có phải beep hay không
            if file_size < 1000:
                print("   ⚠️  File quá nhỏ - có thể là mock/beep")
            elif 40000 <= file_size <= 60000:
                print("   ⚠️  File size giống mock audio (49571 bytes)")
                print("   🔍 Đây có thể là mock audio, không phải Edge TTS thật!")
            else:
                print("   ✅ File size hợp lý - có thể là audio thật")
            
            return True
        else:
            print(f"❌ File không tồn tại: {output_file}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_list_voices():
    """Liệt kê các giọng tiếng Anh có sẵn"""
    print("\n" + "="*70)
    print("📋 DANH SÁCH GIỌNG TIẾNG ANH")
    print("="*70)
    
    try:
        voices = await edge_tts.list_voices()
        
        # Filter English voices
        en_voices = [v for v in voices if v['Locale'].startswith('en-')]
        
        print(f"\nTổng số giọng tiếng Anh: {len(en_voices)}\n")
        
        # Group by locale
        from collections import defaultdict
        by_locale = defaultdict(list)
        
        for v in en_voices:
            locale = v['Locale']
            by_locale[locale].append(v)
        
        # Print by locale
        for locale in sorted(by_locale.keys()):
            locale_voices = by_locale[locale]
            print(f"\n🌍 {locale} ({len(locale_voices)} giọng):")
            for v in locale_voices[:5]:  # Show first 5
                gender = v.get('Gender', 'Unknown')
                name = v['ShortName']
                print(f"   - {name} ({gender})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_multiple_texts():
    """Test với nhiều văn bản khác nhau"""
    print("\n" + "="*70)
    print("📝 TEST VỚI NHIỀU VĂN BẢN")
    print("="*70)
    
    tests = [
        ("Short word", "beautiful"),
        ("Short sentence", "The cat sat on the mat."),
        ("Long sentence", "Machine learning is a subset of artificial intelligence that enables computers to learn from data."),
    ]
    
    for test_name, text in tests:
        print(f"\n🎯 {test_name}: '{text[:50]}...'")
        
        try:
            output_file = f"test_{test_name.replace(' ', '_').lower()}.mp3"
            
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            await communicate.save(output_file)
            
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"   ✅ Generated: {size:,} bytes")
                
                # Check if all files have same size (indicates mock)
                if size == 49571:
                    print(f"   ⚠️  CẢNH BÁO: File size = 49571 bytes (giống mock audio)")
            else:
                print(f"   ❌ Failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 EDGE TTS DIRECT TEST SUITE")
    print("="*70)
    
    # Test 1: Basic generation
    await test_direct_edge_tts()
    
    # Test 2: List voices
    await test_list_voices()
    
    # Test 3: Multiple texts
    await test_multiple_texts()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)
    print("\n💡 Nếu tất cả file đều có size 49571 bytes:")
    print("   -> Có thể bạn đang chạy mock mode không biết")
    print("   -> Hoặc có vấn đề với Edge TTS")
    print("\n💡 Kiểm tra:")
    print("   1. Kết nối internet")
    print("   2. Cài đặt edge-tts: pip install edge-tts")
    print("   3. Version edge-tts: pip show edge-tts")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
