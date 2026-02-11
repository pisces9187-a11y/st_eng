"""
Speech-to-Text Utilities for Pronunciation Assessment

This module provides STT integration for:
- Tongue Twister Challenge pronunciation analysis
- Word-level accuracy detection
- Phoneme-level feedback (Phase 5.2)

Supported Providers:
- Google Cloud Speech-to-Text (default)
- Mock mode for development/testing
"""

import io
import logging
from typing import Dict, List, Optional
from difflib import SequenceMatcher
from django.conf import settings

logger = logging.getLogger(__name__)

# Import phoneme analyzer for Phase 5.2
try:
    from .phoneme_analyzer import analyze_with_phonemes
    PHONEME_ANALYSIS_AVAILABLE = True
except ImportError:
    PHONEME_ANALYSIS_AVAILABLE = False
    logger.warning("Phoneme analyzer not available")


class SpeechToTextService:
    """
    Main STT service with provider abstraction.
    """
    
    def __init__(self, provider: str = 'google'):
        """
        Initialize STT service.
        
        Args:
            provider: 'google', 'azure', 'assemblyai', or 'mock'
        """
        self.provider = provider
        self._client = None
    
    def analyze_pronunciation(
        self, 
        audio_file, 
        expected_text: str,
        language_code: str = 'en-US'
    ) -> Dict:
        """
        Analyze pronunciation from audio file.
        
        Args:
            audio_file: Django File or path to audio file
            expected_text: Expected text (e.g., tongue twister)
            language_code: Language for recognition
        
        Returns:
            {
                'transcript': 'detected text...',
                'words': [
                    {
                        'word': 'she',
                        'confidence': 0.95,
                        'start_time': 0.0,
                        'end_time': 0.3
                    },
                    ...
                ],
                'accuracy': 92.5,  # % match with expected text
                'pronunciation_score': 88.0,  # Overall quality
                'duration': 3.5,  # Audio duration in seconds
                'words_detected': 10,
                'words_expected': 12,
                'speed': 2.86,  # Words per second
            }
        """
        
        if self.provider == 'google':
            return self._google_stt(audio_file, expected_text, language_code)
        elif self.provider == 'mock':
            return self._mock_stt(audio_file, expected_text)
        else:
            raise ValueError(f"Unsupported STT provider: {self.provider}")
    
    def _google_stt(
        self, 
        audio_file, 
        expected_text: str,
        language_code: str
    ) -> Dict:
        """
        Google Cloud Speech-to-Text implementation.
        """
        try:
            from google.cloud import speech_v1p1beta1 as speech
        except ImportError:
            logger.error("google-cloud-speech not installed. Falling back to mock mode.")
            return self._mock_stt(audio_file, expected_text)
        
        try:
            # Initialize client (lazy loading)
            if self._client is None:
                self._client = speech.SpeechClient()
            
            # Read audio content
            if hasattr(audio_file, 'read'):
                # Django File object
                audio_content = audio_file.read()
                if hasattr(audio_file, 'seek'):
                    audio_file.seek(0)  # Reset file pointer
            else:
                # File path
                with io.open(audio_file, 'rb') as f:
                    audio_content = f.read()
            
            # Configure audio
            audio = speech.RecognitionAudio(content=audio_content)
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,  # Browser MediaRecorder default
                sample_rate_hertz=48000,  # Browser default
                language_code=language_code,
                enable_word_time_offsets=True,
                enable_word_confidence=True,
                enable_automatic_punctuation=False,
                model='default',
                use_enhanced=True,
            )
            
            # Perform recognition
            logger.info(f"Starting Google STT for text: {expected_text[:50]}...")
            response = self._client.recognize(config=config, audio=audio)
            
            # Parse results
            if not response.results:
                logger.warning("No speech detected in audio")
                return self._empty_result(expected_text)
            
            result = response.results[0]
            alternative = result.alternatives[0]
            
            # Extract words with metadata
            words = []
            total_duration = 0.0
            
            for word_info in alternative.words:
                word_data = {
                    'word': word_info.word,
                    'confidence': word_info.confidence,
                    'start_time': word_info.start_time.total_seconds(),
                    'end_time': word_info.end_time.total_seconds(),
                }
                words.append(word_data)
                total_duration = max(total_duration, word_data['end_time'])
            
            # Calculate accuracy
            accuracy = self._calculate_accuracy(expected_text, alternative.transcript)
            
            # Calculate pronunciation score from word confidences
            if words:
                pronunciation_score = sum(w['confidence'] for w in words) / len(words) * 100
            else:
                pronunciation_score = 0
            
            # Calculate metrics
            words_detected = len(words)
            words_expected = len(expected_text.split())
            speed = words_detected / total_duration if total_duration > 0 else 0
            
            logger.info(f"STT Success - Detected: '{alternative.transcript}', Accuracy: {accuracy:.1f}%")
            
            return {
                'transcript': alternative.transcript,
                'words': words,
                'accuracy': accuracy,
                'pronunciation_score': pronunciation_score,
                'duration': total_duration,
                'words_detected': words_detected,
                'words_expected': words_expected,
                'speed': speed,
            }
            
        except Exception as e:
            logger.error(f"Google STT error: {str(e)}", exc_info=True)
            # Fallback to mock
            return self._mock_stt(audio_file, expected_text)
    
    def _mock_stt(self, audio_file, expected_text: str) -> Dict:
        """
        Mock STT for development/testing without API.
        
        Simulates realistic results based on expected text.
        """
        import random
        
        words_expected = expected_text.split()
        num_words = len(words_expected)
        
        # Simulate detection (80-95% of words detected)
        detection_rate = random.uniform(0.80, 0.95)
        words_detected = int(num_words * detection_rate)
        
        # Simulate duration (0.3-0.5 seconds per word)
        duration = num_words * random.uniform(0.3, 0.5)
        
        # Simulate word-level data
        words = []
        current_time = 0.0
        
        for i, word in enumerate(words_expected[:words_detected]):
            word_duration = random.uniform(0.2, 0.6)
            confidence = random.uniform(0.85, 0.98)
            
            words.append({
                'word': word.lower(),
                'confidence': confidence,
                'start_time': current_time,
                'end_time': current_time + word_duration,
            })
            
            current_time += word_duration + random.uniform(0.05, 0.15)  # Add pause
        
        # Calculate metrics
        accuracy = (words_detected / num_words) * 100
        pronunciation_score = sum(w['confidence'] for w in words) / len(words) * 100 if words else 0
        speed = words_detected / duration if duration > 0 else 0
        
        # Generate transcript
        transcript = ' '.join(w['word'] for w in words)
        
        logger.info(f"Mock STT - Detected {words_detected}/{num_words} words, Accuracy: {accuracy:.1f}%")
        
        return {
            'transcript': transcript,
            'words': words,
            'accuracy': accuracy,
            'pronunciation_score': pronunciation_score,
            'duration': duration,
            'words_detected': words_detected,
            'words_expected': num_words,
            'speed': speed,
        }
    
    def _calculate_accuracy(self, expected: str, detected: str) -> float:
        """
        Calculate text matching accuracy using SequenceMatcher.
        
        Args:
            expected: Expected text
            detected: Detected text from STT
        
        Returns:
            Accuracy percentage (0-100)
        """
        # Normalize texts
        expected_words = expected.lower().split()
        detected_words = detected.lower().split()
        
        # Use SequenceMatcher for fuzzy matching
        matcher = SequenceMatcher(None, expected_words, detected_words)
        similarity = matcher.ratio()
        
        return similarity * 100
    
    def _empty_result(self, expected_text: str) -> Dict:
        """
        Return empty result when no speech detected.
        """
        num_words = len(expected_text.split())
        
        return {
            'transcript': '',
            'words': [],
            'accuracy': 0,
            'pronunciation_score': 0,
            'duration': 0,
            'words_detected': 0,
            'words_expected': num_words,
            'speed': 0,
        }


def get_stt_service() -> SpeechToTextService:
    """
    Factory function to get configured STT service.
    
    Returns:
        Configured SpeechToTextService instance
    """
    # Check if STT is enabled in settings
    use_stt = getattr(settings, 'USE_SPEECH_TO_TEXT', False)
    provider = getattr(settings, 'STT_PROVIDER', 'mock')
    
    if not use_stt:
        provider = 'mock'
    
    return SpeechToTextService(provider=provider)


def analyze_tongue_twister_audio(audio_file, twister_text: str, enable_phoneme_analysis: bool = True) -> Dict:
    """
    Convenience function to analyze tongue twister audio.
    
    Args:
        audio_file: Audio file to analyze
        twister_text: Expected tongue twister text
        enable_phoneme_analysis: Enable Phase 5.2 phoneme-level analysis
    
    Returns:
        Analysis results with scores and metrics (+ phoneme analysis if enabled)
    """
    stt = get_stt_service()
    result = stt.analyze_pronunciation(audio_file, twister_text)
    
    # Phase 5.2: Add phoneme-level analysis
    if enable_phoneme_analysis and PHONEME_ANALYSIS_AVAILABLE:
        try:
            result = analyze_with_phonemes(result, twister_text)
            logger.info(f"Phoneme analysis added: {result.get('phoneme_analysis', {}).get('total_issues', 0)} issues found")
        except Exception as e:
            logger.warning(f"Phoneme analysis failed: {str(e)}")
    
    return result


def generate_pronunciation_feedback(
    stt_result: Dict,
    difficulty: int = 3
) -> str:
    """
    Generate detailed feedback based on STT results.
    
    Args:
        stt_result: Result from analyze_pronunciation()
        difficulty: Tongue twister difficulty (1-5)
    
    Returns:
        Human-readable feedback message
    """
    accuracy = stt_result['accuracy']
    speed = stt_result['speed']
    pronunciation_score = stt_result['pronunciation_score']
    words_detected = stt_result['words_detected']
    words_expected = stt_result['words_expected']
    
    feedback_parts = []
    
    # Overall assessment
    if accuracy >= 95:
        feedback_parts.append("🎉 Xuất sắc! Phát âm rất chính xác.")
    elif accuracy >= 85:
        feedback_parts.append("👍 Tốt! Phát âm khá chính xác.")
    elif accuracy >= 70:
        feedback_parts.append("💪 Được! Còn cần luyện tập thêm.")
    else:
        feedback_parts.append("📖 Hãy đọc chậm và rõ ràng hơn.")
    
    # Speed assessment
    expected_speed = 2.5  # words per second (baseline)
    
    if speed < expected_speed * 0.7:
        feedback_parts.append("Bạn đọc hơi chậm. Thử tăng tốc độ nhẹ!")
    elif speed > expected_speed * 1.5:
        feedback_parts.append("Bạn đọc hơi nhanh. Thử giảm tốc để phát âm rõ hơn!")
    else:
        feedback_parts.append("Tốc độ đọc rất tốt!")
    
    # Word detection assessment
    if words_detected < words_expected:
        missing = words_expected - words_detected
        feedback_parts.append(f"Thiếu {missing} từ - hãy đọc đủ câu!")
    
    # Pronunciation quality
    if pronunciation_score >= 90:
        feedback_parts.append("Phát âm từng từ rất rõ ràng! ✨")
    elif pronunciation_score >= 75:
        feedback_parts.append("Phát âm khá tốt, một số từ còn mơ hồ.")
    else:
        feedback_parts.append("Cần tập trung phát âm rõ từng từ hơn.")
    
    # Difficulty-based encouragement
    if difficulty >= 4:
        if accuracy >= 80:
            feedback_parts.append("Với độ khó này, kết quả của bạn rất ấn tượng! 🌟")
        else:
            feedback_parts.append("Đây là câu khó, đừng nản! Cứ luyện tập!")
    
    return " ".join(feedback_parts)
