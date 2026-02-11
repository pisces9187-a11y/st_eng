"""
Test script for Phase 5.2 Phoneme Analyzer Module
Tests phoneme detection, error identification, and Vietnamese learner recommendations
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.curriculum.phoneme_analyzer import (
    PhonemeAnalyzer,
    get_phoneme_analyzer,
    analyze_with_phonemes,
    PHONEME_PATTERNS,
    COMMON_ERRORS
)


def test_phoneme_detection():
    """Test 1: Phoneme pattern detection in text"""
    print("\n" + "="*60)
    print("TEST 1: Phoneme Detection")
    print("="*60)
    
    analyzer = get_phoneme_analyzer()
    
    # Test with common Vietnamese problem sounds
    test_text = "She thought three things through thoroughly"
    
    detected = analyzer.analyze_text_for_phonemes(test_text)
    
    print(f"Text: {test_text}")
    print(f"\nDetected {len(detected)} phoneme instances:")
    
    # Group by phoneme for display
    from collections import defaultdict
    phoneme_groups = defaultdict(list)
    for item in detected:
        phoneme_groups[item['phoneme']].append(item['word'])
    
    for phoneme, words in phoneme_groups.items():
        print(f"  /{phoneme}/ in words: {', '.join(set(words))}")
    
    # Verify θ (th) is detected
    phonemes_found = [item['phoneme'] for item in detected]
    assert 'θ' in phonemes_found or 'ð' in phonemes_found, "Failed to detect /θ/ or /ð/ sounds"
    
    # Count th words
    th_words = [item['word'] for item in detected if item['phoneme'] in ['θ', 'ð']]
    assert len(th_words) >= 3, f"Expected 3+ 'th' words, found {len(th_words)}"
    
    print(f"\n✅ PASS: Detected {len(detected)} phoneme instances across {len(phoneme_groups)} unique phonemes")
    return True


def test_problem_identification():
    """Test 2: Identify problem phonemes from low confidence words"""
    print("\n" + "="*60)
    print("TEST 2: Problem Phoneme Identification")
    print("="*60)
    
    analyzer = get_phoneme_analyzer()
    
    # Mock data
    expected_text = "think this ship happy"
    detected_words = ["think", "this", "ship", "happy"]
    word_confidences = [0.55, 0.62, 0.71, 0.95]  # Low to high
    
    problems = analyzer.identify_problem_phonemes(
        expected_text,
        detected_words,
        word_confidences
    )
    
    print(f"Text: {expected_text}")
    print(f"\nIdentified {len(problems)} problem phoneme instances:")
    
    # Group by phoneme
    from collections import defaultdict
    problem_groups = defaultdict(list)
    for problem in problems:
        problem_groups[problem['phoneme']].append(problem['word'])
    
    for phoneme, words in problem_groups.items():
        print(f"  /{phoneme}/ in: {', '.join(set(words))}")
    
    # Verify problem phonemes are identified
    phonemes_found = [p['phoneme'] for p in problems]
    assert len(phonemes_found) > 0, "Should identify at least one problem phoneme"
    
    # The low confidence words should have problems detected
    problem_words = [p['word'] for p in problems]
    assert 'think' in problem_words or 'this' in problem_words, \
        "Should identify problems in low-confidence words"
    
    print(f"\n✅ PASS: Identified problems in {len(set(problem_words))} unique words")
    return True


def test_recommendation_generation():
    """Test 3: Generate Vietnamese learner recommendations"""
    print("\n" + "="*60)
    print("TEST 3: Vietnamese Learner Recommendations")
    print("="*60)
    
    analyzer = get_phoneme_analyzer()
    
    # Mock problem phonemes with correct structure (includes 'word' key)
    problem_phonemes = [
        {'phoneme': 'θ', 'word': 'think'},
        {'phoneme': 'θ', 'word': 'thought'},
        {'phoneme': 'θ', 'word': 'through'},
        {'phoneme': 'ð', 'word': 'this'},
        {'phoneme': 'ð', 'word': 'that'},
        {'phoneme': 'r', 'word': 'right'},
    ]
    
    recommendations = analyzer.generate_phoneme_recommendations(problem_phonemes)
    
    print(f"\nGenerated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. Phoneme: /{rec['ipa_symbol']}/ - Priority: {rec['priority']}")
        print(f"   Affected words: {', '.join(rec['affected_words'])}")
        print(f"   Frequency: {rec['frequency']}")
        print(f"   Tip: {rec['tip'][:60]}...")
        if rec.get('vietnamese_note'):
            print(f"   Vietnamese note: {rec['vietnamese_note'][:60]}...")
    
    # Verify top priority
    assert recommendations[0]['phoneme'] == 'θ', "θ should be highest priority (freq 3)"
    assert recommendations[0]['priority'] == 'high', "θ should be high priority"
    assert recommendations[0]['frequency'] == 3, "θ should have frequency 3"
    
    # Verify affected words
    assert set(recommendations[0]['affected_words']) == {'think', 'thought', 'through'}, \
        "θ should affect 'think', 'thought', 'through'"
    
    # Verify tips exist
    for rec in recommendations:
        assert rec['tip'], f"Missing tip for /{rec['phoneme']}/"
    
    print("\n✅ PASS: Recommendation generation works correctly")
    return True


def test_full_integration():
    """Test 4: Full integration with STT result"""
    print("\n" + "="*60)
    print("TEST 4: Full Integration with STT Result")
    print("="*60)
    
    # Mock STT result from Phase 5.1
    mock_stt_result = {
        'transcript': 'She sells sea shells by the sea shore',
        'confidence': 0.78,
        'duration': 3.5,
        'word_details': [
            {'word': 'She', 'confidence': 0.95},
            {'word': 'sells', 'confidence': 0.88},
            {'word': 'sea', 'confidence': 0.92},
            {'word': 'shells', 'confidence': 0.65},  # Low - ʃ problem
            {'word': 'by', 'confidence': 0.94},
            {'word': 'the', 'confidence': 0.72},     # Low - ð problem
            {'word': 'sea', 'confidence': 0.91},
            {'word': 'shore', 'confidence': 0.68}    # Low - ʃ problem
        ],
        'score': 78
    }
    
    text = "She sells sea shells by the sea shore"
    
    # Run full analysis
    enhanced_result = analyze_with_phonemes(mock_stt_result, text)
    
    print(f"Original transcript: {text}")
    print(f"STT confidence: {enhanced_result['confidence']:.2%}")
    
    # Check phoneme analysis added
    assert 'phoneme_analysis' in enhanced_result, "Phoneme analysis not added"
    
    phoneme_analysis = enhanced_result['phoneme_analysis']
    print(f"\nPhoneme Analysis:")
    print(f"  Total issues: {phoneme_analysis['total_issues']}")
    print(f"  Unique phonemes: {phoneme_analysis['unique_phonemes']}")
    print(f"  Recommendations: {len(phoneme_analysis['recommendations'])}")
    
    if phoneme_analysis['recommendations']:
        print(f"\nTop recommendation:")
        top_rec = phoneme_analysis['recommendations'][0]
        print(f"  Phoneme: /{top_rec['ipa_symbol']}/ ({top_rec['priority']} priority)")
        print(f"  Frequency: {top_rec['frequency']}")
        print(f"  Affected: {', '.join(top_rec['affected_words'])}")
        print(f"  Tip: {top_rec['tip'][:80]}...")
    
    # Verify structure
    assert phoneme_analysis['total_issues'] > 0, "Should have detected issues"
    assert phoneme_analysis['unique_phonemes'] > 0, "Should have unique phonemes"
    assert len(phoneme_analysis['recommendations']) > 0, "Should have recommendations"
    
    # Verify /ʃ/ is identified (appears in 'shells' and 'shore')
    phonemes_in_recs = [r['phoneme'] for r in phoneme_analysis['recommendations']]
    assert 'ʃ' in phonemes_in_recs, "Should identify /ʃ/ problem in 'shells' and 'shore'"
    
    print("\n✅ PASS: Full integration works correctly")
    return True


def test_vietnamese_errors_database():
    """Test 5: Vietnamese learner error database"""
    print("\n" + "="*60)
    print("TEST 5: Vietnamese Learner Error Database")
    print("="*60)
    
    print(f"\nTotal phoneme patterns: {len(PHONEME_PATTERNS)}")
    print(f"Vietnamese problem phonemes: {len(COMMON_ERRORS)}")
    
    print(f"\nVietnamese challenging phonemes:")
    for phoneme, error_data in COMMON_ERRORS.items():
        # Use substitutions instead of description
        substitutions = error_data.get('substitutions', [])
        print(f"\n  /{phoneme}/ - Common substitutions: {', '.join(substitutions)}")
        print(f"    Tip: {error_data.get('tip', 'N/A')[:70]}...")
    
    # Verify critical phonemes are included
    critical_phonemes = ['θ', 'ð', 'r', 'l', 'v', 'w']
    for phoneme in critical_phonemes:
        assert phoneme in COMMON_ERRORS, f"Critical phoneme /{phoneme}/ missing from COMMON_ERRORS"
    
    # Verify all have tips
    for phoneme, error_data in COMMON_ERRORS.items():
        assert error_data.get('tip'), f"Missing tip for /{phoneme}/"
        assert error_data.get('substitutions'), f"Missing substitutions for /{phoneme}/"
    
    print("\n✅ PASS: Vietnamese error database is complete")
    return True


def test_priority_assignment():
    """Test 6: Priority level assignment logic"""
    print("\n" + "="*60)
    print("TEST 6: Priority Level Assignment")
    print("="*60)
    
    analyzer = get_phoneme_analyzer()
    
    # Test with different frequencies (correct structure with 'word' key)
    problem_phonemes = [
        # High frequency (5 occurrences)
        {'phoneme': 'θ', 'word': 'think'},
        {'phoneme': 'θ', 'word': 'thought'},
        {'phoneme': 'θ', 'word': 'three'},
        {'phoneme': 'θ', 'word': 'throw'},
        {'phoneme': 'θ', 'word': 'through'},
        # Medium frequency (2 occurrences)
        {'phoneme': 'ð', 'word': 'this'},
        {'phoneme': 'ð', 'word': 'that'},
        # Low frequency (1 occurrence)
        {'phoneme': 'r', 'word': 'right'},
    ]
    
    recommendations = analyzer.generate_phoneme_recommendations(problem_phonemes)
    
    # Expected priorities based on frequency
    expected = {
        'θ': ('high', 5),   # >= 3
        'ð': ('medium', 2), # >= 2
        'r': ('low', 1),    # < 2
    }
    
    print("\nPriority assignments:")
    for rec in recommendations:
        phoneme = rec['phoneme']
        priority = rec['priority']
        freq = rec['frequency']
        
        expected_priority, expected_freq = expected.get(phoneme, (None, None))
        
        print(f"  /{phoneme}/ - Frequency: {freq} → Priority: {priority}")
        
        if expected_priority:
            assert priority == expected_priority, \
                f"Priority mismatch for /{phoneme}/: expected {expected_priority}, got {priority}"
            assert freq == expected_freq, \
                f"Frequency mismatch for /{phoneme}/: expected {expected_freq}, got {freq}"
    
    print("\n✅ PASS: Priority assignment logic works correctly")
    return True


def run_all_tests():
    """Run all phoneme analyzer tests"""
    print("\n" + "="*70)
    print("PHASE 5.2 - PHONEME ANALYZER TEST SUITE")
    print("Testing phoneme detection for Vietnamese learners")
    print("="*70)
    
    tests = [
        ("Phoneme Detection", test_phoneme_detection),
        ("Problem Identification", test_problem_identification),
        ("Recommendation Generation", test_recommendation_generation),
        ("Full Integration", test_full_integration),
        ("Vietnamese Error Database", test_vietnamese_errors_database),
        ("Priority Assignment", test_priority_assignment),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except AssertionError as e:
            print(f"\n❌ FAIL: {e}")
            results.append((test_name, False))
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 5.2 phoneme analyzer is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
