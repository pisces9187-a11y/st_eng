#!/usr/bin/env python3
"""
Quick test script for Speech-to-Text module (Phase 5)
Tests STT integration without needing full Django server.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.curriculum.speech_to_text import get_stt_service, analyze_tongue_twister_audio


def test_mock_stt():
    """Test mock STT mode (default)"""
    print("=" * 70)
    print("🧪 TESTING MOCK STT MODE")
    print("=" * 70)
    
    # Create mock audio file
    from django.core.files.uploadedfile import SimpleUploadedFile
    mock_audio = SimpleUploadedFile("test.webm", b"fake audio data", content_type="audio/webm")
    
    # Test text
    test_text = "She sells seashells by the seashore"
    
    print(f"\n📝 Expected Text: \"{test_text}\"")
    print(f"🎤 Audio File: Mock WebM file ({len(mock_audio)} bytes)")
    
    # Analyze
    try:
        result = analyze_tongue_twister_audio(mock_audio, test_text)
        
        print(f"\n✅ STT Analysis Complete!")
        print(f"\n📊 Results:")
        print(f"   Transcript: \"{result['transcript']}\"")
        print(f"   Accuracy: {result['accuracy']:.1f}%")
        print(f"   Pronunciation Score: {result['pronunciation_score']:.1f}")
        print(f"   Duration: {result['duration']:.2f}s")
        print(f"   Words Detected: {result['words_detected']}/{result['words_expected']}")
        print(f"   Speed: {result['speed']:.2f} words/second")
        
        print(f"\n🔤 Word Details:")
        for i, word in enumerate(result['words'][:5], 1):  # Show first 5 words
            print(f"   {i}. '{word['word']}' - Confidence: {word['confidence']*100:.0f}% "
                  f"[{word['start_time']:.2f}s - {word['end_time']:.2f}s]")
        
        if len(result['words']) > 5:
            print(f"   ... and {len(result['words']) - 5} more words")
        
        print(f"\n✅ Mock STT Test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_stt_service():
    """Test STT service initialization"""
    print("\n" + "=" * 70)
    print("🔧 TESTING STT SERVICE INITIALIZATION")
    print("=" * 70)
    
    try:
        from django.conf import settings
        
        print(f"\n⚙️  Settings:")
        print(f"   USE_SPEECH_TO_TEXT: {getattr(settings, 'USE_SPEECH_TO_TEXT', False)}")
        print(f"   STT_PROVIDER: {getattr(settings, 'STT_PROVIDER', 'mock')}")
        
        stt = get_stt_service()
        print(f"\n✅ STT Service Initialized!")
        print(f"   Provider: {stt.provider}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_feedback_generation():
    """Test feedback generation"""
    print("\n" + "=" * 70)
    print("🗣️  TESTING FEEDBACK GENERATION")
    print("=" * 70)
    
    try:
        from apps.curriculum.speech_to_text import generate_pronunciation_feedback
        
        # Test case 1: Excellent performance
        result1 = {
            'accuracy': 95,
            'speed': 2.5,
            'pronunciation_score': 92,
            'words_detected': 10,
            'words_expected': 10,
            'duration': 4.0
        }
        
        feedback1 = generate_pronunciation_feedback(result1, difficulty=3)
        print(f"\n✅ Test 1 - Excellent (95% accuracy):")
        print(f"   {feedback1}")
        
        # Test case 2: Average performance
        result2 = {
            'accuracy': 75,
            'speed': 1.8,
            'pronunciation_score': 70,
            'words_detected': 8,
            'words_expected': 10,
            'duration': 5.5
        }
        
        feedback2 = generate_pronunciation_feedback(result2, difficulty=4)
        print(f"\n✅ Test 2 - Average (75% accuracy):")
        print(f"   {feedback2}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🎉" * 35)
    print(" " * 10 + "PHASE 5: STT INTEGRATION TEST SUITE")
    print("🎉" * 35)
    
    tests = [
        ("STT Service Initialization", test_stt_service),
        ("Mock STT Analysis", test_mock_stt),
        ("Feedback Generation", test_feedback_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}  {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n🎯 Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! STT integration is working correctly!")
        print("\n💡 Next steps:")
        print("   1. Test on web interface: http://localhost:8000/pronunciation/tongue-twister/")
        print("   2. Record audio and check transcript display")
        print("   3. Verify word-level highlights")
        print("   4. (Optional) Enable real Google STT with credentials")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
