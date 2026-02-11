"""
Phase 5.2: Phoneme-level Analysis
Detailed pronunciation feedback with phoneme identification.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)

# IPA to common spelling patterns mapping
PHONEME_PATTERNS = {
    # Vowels
    'iː': ['ee', 'ea', 'e', 'ie'],  # /iː/ - see, sea, be, piece
    'ɪ': ['i', 'y', 'e'],  # /ɪ/ - sit, gym, pretty
    'e': ['e', 'ea'],  # /e/ - bed, head
    'æ': ['a'],  # /æ/ - cat
    'ɑː': ['a', 'ar'],  # /ɑː/ - car, father
    'ɒ': ['o'],  # /ɒ/ - hot
    'ɔː': ['or', 'aw', 'au'],  # /ɔː/ - for, saw, caught
    'ʊ': ['oo', 'u'],  # /ʊ/ - book, put
    'uː': ['oo', 'u', 'ew'],  # /uː/ - food, rude, few
    'ʌ': ['u', 'o'],  # /ʌ/ - cup, son
    'ɜː': ['er', 'ur', 'ir'],  # /ɜː/ - her, turn, bird
    'ə': ['a', 'e', 'o'],  # /ə/ - about, happen, lemon
    
    # Consonants
    'p': ['p'],
    'b': ['b'],
    't': ['t'],
    'd': ['d'],
    'k': ['k', 'c', 'ck'],
    'g': ['g'],
    'f': ['f', 'ph'],
    'v': ['v'],
    'θ': ['th'],  # /θ/ - think
    'ð': ['th'],  # /ð/ - this
    's': ['s', 'c'],
    'z': ['z', 's'],
    'ʃ': ['sh', 'ti', 'ci'],  # /ʃ/ - ship, nation, special
    'ʒ': ['s', 'si'],  # /ʒ/ - vision, measure
    'h': ['h'],
    'tʃ': ['ch', 'tch'],  # /tʃ/ - church, catch
    'dʒ': ['j', 'g', 'dge'],  # /dʒ/ - judge, gentle, edge
    'm': ['m'],
    'n': ['n'],
    'ŋ': ['ng', 'n'],  # /ŋ/ - sing, think
    'l': ['l'],
    'r': ['r'],
    'j': ['y'],  # /j/ - yes
    'w': ['w'],
}

# Common phoneme errors and their causes
COMMON_ERRORS = {
    'θ': {
        'substitutions': ['s', 't', 'f'],
        'tip': 'Đặt lưỡi giữa răng trên và dưới, thổi khí nhẹ',
        'vietnamese_equivalent': 'Không có âm tương đương trong tiếng Việt'
    },
    'ð': {
        'substitutions': ['d', 'z', 'v'],
        'tip': 'Giống /θ/ nhưng có rung thanh quản',
        'vietnamese_equivalent': 'Không có âm tương đương trong tiếng Việt'
    },
    'ʃ': {
        'substitutions': ['s', 'tʃ'],
        'tip': 'Môi tròn, lưỡi gần vòm miệng',
        'vietnamese_equivalent': 'Gần giống "s" nhưng môi tròn hơn'
    },
    'ʒ': {
        'substitutions': ['z', 'dʒ'],
        'tip': 'Giống /ʃ/ nhưng có rung thanh quản',
        'vietnamese_equivalent': 'Không có âm tương đương'
    },
    'r': {
        'substitutions': ['l', 'w'],
        'tip': 'Cuộn lưỡi lên, không chạm vòm miệng',
        'vietnamese_equivalent': 'Khác với "r" tiếng Việt'
    },
    'l': {
        'substitutions': ['r', 'n'],
        'tip': 'Chạm lưỡi vào vòm miệng phía trước',
        'vietnamese_equivalent': 'Tương tự "l" tiếng Việt'
    },
    'v': {
        'substitutions': ['w', 'b'],
        'tip': 'Răng trên chạm môi dưới, có rung',
        'vietnamese_equivalent': 'Tương tự "v" tiếng Việt'
    },
    'w': {
        'substitutions': ['v', 'u'],
        'tip': 'Môi tròn, không chạm răng',
        'vietnamese_equivalent': 'Gần giống "u" ngắn'
    },
}


class PhonemeAnalyzer:
    """
    Analyze pronunciation at phoneme level.
    """
    
    def __init__(self):
        self.phoneme_patterns = PHONEME_PATTERNS
        self.common_errors = COMMON_ERRORS
    
    def analyze_text_for_phonemes(self, text: str) -> List[Dict]:
        """
        Analyze text to identify key phonemes.
        
        Args:
            text: Text to analyze (e.g., "She sells seashells")
        
        Returns:
            List of phoneme information
        """
        # Convert to lowercase for analysis
        text_lower = text.lower()
        words = text_lower.split()
        
        detected_phonemes = []
        
        # Detect key phonemes based on common patterns
        for word in words:
            word_phonemes = self._detect_word_phonemes(word)
            for phoneme_info in word_phonemes:
                phoneme_info['word'] = word
                detected_phonemes.append(phoneme_info)
        
        return detected_phonemes
    
    def _detect_word_phonemes(self, word: str) -> List[Dict]:
        """
        Detect phonemes in a single word based on spelling patterns.
        """
        phonemes = []
        
        # Check for common patterns
        checks = [
            # TH sounds
            (r'th', ['θ', 'ð']),  # think, this
            # SH sound
            (r'sh|tion|sion', ['ʃ']),  # ship, nation, vision
            # CH sound
            (r'ch|tch', ['tʃ']),  # church, catch
            # NG sound
            (r'ng', ['ŋ']),  # sing
            # Double EE
            (r'ee|ea', ['iː']),  # see, sea
            # S at start
            (r'^s', ['s']),  # sell
            # R sound
            (r'r', ['r']),  # red
            # L sound
            (r'l', ['l']),  # shell
        ]
        
        for pattern, possible_phonemes in checks:
            matches = re.finditer(pattern, word)
            for match in matches:
                for phoneme in possible_phonemes:
                    phonemes.append({
                        'phoneme': phoneme,
                        'position': match.start(),
                        'spelling': match.group()
                    })
        
        return phonemes
    
    def identify_problem_phonemes(
        self, 
        expected_text: str,
        detected_words: List[str],
        word_confidences: List[float]
    ) -> List[Dict]:
        """
        Identify phonemes that likely caused pronunciation issues.
        
        Args:
            expected_text: Expected text
            detected_words: Words detected by STT
            word_confidences: Confidence scores for each word
        
        Returns:
            List of problem phonemes with details
        """
        expected_words = expected_text.lower().split()
        problem_phonemes = []
        
        # Analyze each expected word
        for i, expected_word in enumerate(expected_words):
            if i >= len(detected_words):
                # Word was completely missed
                word_phonemes = self._detect_word_phonemes(expected_word)
                for phoneme_info in word_phonemes:
                    problem_phonemes.append({
                        'phoneme': phoneme_info['phoneme'],
                        'word': expected_word,
                        'issue': 'word_missed',
                        'severity': 'high',
                        'confidence': 0.0
                    })
            elif i < len(word_confidences) and word_confidences[i] < 0.85:
                # Word had low confidence - likely pronunciation issue
                detected_word = detected_words[i]
                
                # Compare expected vs detected
                if expected_word != detected_word:
                    # Words are different - find phoneme differences
                    word_phonemes = self._detect_word_phonemes(expected_word)
                    for phoneme_info in word_phonemes:
                        problem_phonemes.append({
                            'phoneme': phoneme_info['phoneme'],
                            'word': expected_word,
                            'issue': 'mispronounced',
                            'severity': 'medium' if word_confidences[i] > 0.7 else 'high',
                            'confidence': word_confidences[i],
                            'detected_as': detected_word
                        })
                else:
                    # Same word but low confidence - unclear pronunciation
                    word_phonemes = self._detect_word_phonemes(expected_word)
                    for phoneme_info in word_phonemes:
                        problem_phonemes.append({
                            'phoneme': phoneme_info['phoneme'],
                            'word': expected_word,
                            'issue': 'unclear',
                            'severity': 'low',
                            'confidence': word_confidences[i]
                        })
        
        return problem_phonemes
    
    def generate_phoneme_recommendations(
        self, 
        problem_phonemes: List[Dict]
    ) -> List[Dict]:
        """
        Generate practice recommendations based on problem phonemes.
        
        Args:
            problem_phonemes: List of problematic phonemes
        
        Returns:
            List of recommendations with practice tips
        """
        # Count phoneme issues
        phoneme_counts = Counter(p['phoneme'] for p in problem_phonemes)
        
        recommendations = []
        
        for phoneme, count in phoneme_counts.most_common(5):  # Top 5
            error_info = self.common_errors.get(phoneme, {})
            
            # Get affected words
            affected_words = [p['word'] for p in problem_phonemes if p['phoneme'] == phoneme]
            
            recommendation = {
                'phoneme': phoneme,
                'ipa_symbol': phoneme,
                'frequency': count,
                'affected_words': list(set(affected_words)),
                'tip': error_info.get('tip', 'Luyện tập âm này nhiều hơn'),
                'vietnamese_note': error_info.get('vietnamese_equivalent', ''),
                'common_mistakes': error_info.get('substitutions', []),
                'priority': 'high' if count >= 3 else 'medium' if count >= 2 else 'low'
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def link_to_phoneme_lessons(self, phoneme_symbol: str) -> Optional[Dict]:
        """
        Link a phoneme to its lesson in the database.
        
        Args:
            phoneme_symbol: IPA symbol (e.g., 'θ', 's', 'ʃ')
        
        Returns:
            Phoneme lesson info if found
        """
        try:
            from apps.curriculum.models import Phoneme
            
            # Try to find phoneme in database
            phoneme = Phoneme.objects.filter(ipa_symbol=phoneme_symbol).first()
            
            if phoneme:
                return {
                    'id': phoneme.id,
                    'ipa_symbol': phoneme.ipa_symbol,
                    'vietnamese_approx': phoneme.vietnamese_approx or '',
                    'phoneme_type': phoneme.get_phoneme_type_display(),
                    'lesson_url': f'/pronunciation/phoneme/{phoneme.ipa_symbol}/',
                    'has_audio': bool(phoneme.audio_sample)
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not link phoneme {phoneme_symbol}: {str(e)}")
            return None
    
    def analyze_pronunciation_with_phonemes(
        self,
        stt_result: Dict,
        expected_text: str
    ) -> Dict:
        """
        Enhanced analysis with phoneme-level details.
        
        Args:
            stt_result: Result from STT service
            expected_text: Expected text
        
        Returns:
            Enhanced result with phoneme analysis
        """
        # Extract word information
        detected_words = [w['word'] for w in stt_result.get('words', [])]
        word_confidences = [w['confidence'] for w in stt_result.get('words', [])]
        
        # Identify problem phonemes
        problem_phonemes = self.identify_problem_phonemes(
            expected_text,
            detected_words,
            word_confidences
        )
        
        # Generate recommendations
        recommendations = self.generate_phoneme_recommendations(problem_phonemes)
        
        # Link to lessons
        for rec in recommendations:
            lesson_info = self.link_to_phoneme_lessons(rec['phoneme'])
            if lesson_info:
                rec['lesson'] = lesson_info
        
        # Add to result
        enhanced_result = stt_result.copy()
        enhanced_result['phoneme_analysis'] = {
            'problem_phonemes': problem_phonemes,
            'recommendations': recommendations,
            'total_issues': len(problem_phonemes),
            'unique_phonemes': len(set(p['phoneme'] for p in problem_phonemes))
        }
        
        return enhanced_result


def get_phoneme_analyzer() -> PhonemeAnalyzer:
    """
    Factory function to get phoneme analyzer.
    """
    return PhonemeAnalyzer()


def analyze_with_phonemes(stt_result: Dict, expected_text: str) -> Dict:
    """
    Convenience function to add phoneme analysis to STT result.
    
    Args:
        stt_result: STT analysis result
        expected_text: Expected text
    
    Returns:
        Enhanced result with phoneme-level analysis
    """
    analyzer = get_phoneme_analyzer()
    return analyzer.analyze_pronunciation_with_phonemes(stt_result, expected_text)
