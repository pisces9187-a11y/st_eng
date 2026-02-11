"""
Unit tests for PhonemeAudioService.

Tests:
- Audio retrieval with fallback logic
- Cache hit/miss behavior
- Bulk operations
- Quality scoring
- Missing audio detection
- Preferred audio handling
"""

from django.test import TestCase
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from apps.curriculum.models import (
    Phoneme,
    PhonemeCategory,
    AudioSource,
    AudioCache,
)
from apps.curriculum.services.audio_service import PhonemeAudioService


class PhonemeAudioServiceTestCase(TestCase):
    """Test PhonemeAudioService functionality."""
    
    def setUp(self):
        """Create test fixtures."""
        # Clear cache before each test
        cache.clear()
        
        # Create service instance
        self.service = PhonemeAudioService()
        
        # Create phoneme category
        self.category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            category_type='vowel',
            order=1
        )
        
        # Create test phonemes
        self.phoneme1 = Phoneme.objects.create(
            category=self.category,
            ipa_symbol='i:',
            vietnamese_approx='vé kéo dài',
            pronunciation_tips_vi='Nguyên âm dài i:',
            order=1
        )
        
        self.phoneme2 = Phoneme.objects.create(
            category=self.category,
            ipa_symbol='ɪ',
            vietnamese_approx='i (ngắn)',
            pronunciation_tips_vi='Nguyên âm ngắn ɪ',
            order=2
        )
        
        self.phoneme3 = Phoneme.objects.create(
            category=self.category,
            ipa_symbol='æ',
            vietnamese_approx='ê (ngắn)',
            pronunciation_tips_vi='Nguyên âm æ',
            order=3
        )
    
    def test_get_native_audio(self):
        """Test getting native speaker audio (highest priority)."""
        # Create native audio
        native = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3',
            audio_duration=1.5
        )
        
        # Get audio
        audio = self.service.get_audio_for_phoneme(self.phoneme1)
        
        # Should return native audio
        self.assertIsNotNone(audio)
        self.assertEqual(audio.id, native.id)
        self.assertEqual(audio.source_type, 'native')
        self.assertEqual(audio.get_quality_score(), 100)
    
    def test_fallback_to_tts(self):
        """Test fallback from native to TTS when native unavailable."""
        # Create only TTS audio (no native)
        tts = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='tts',
            audio_file='phonemes/audio/i_tts.mp3',
            cached_until=timezone.now() + timedelta(days=30)
        )
        
        # Get audio
        audio = self.service.get_audio_for_phoneme(self.phoneme1)
        
        # Should fallback to TTS
        self.assertIsNotNone(audio)
        self.assertEqual(audio.id, tts.id)
        self.assertEqual(audio.source_type, 'tts')
        self.assertEqual(audio.get_quality_score(), 90)
    
    def test_no_audio_available(self):
        """Test when no audio is available."""
        # Don't create any audio sources
        
        # Get audio
        audio = self.service.get_audio_for_phoneme(self.phoneme1)
        
        # Should return None
        self.assertIsNone(audio)
    
    def test_prefer_native_over_tts(self):
        """Test that native is preferred even when TTS exists."""
        # Create both native and TTS
        native = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        tts = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='tts',
            audio_file='phonemes/audio/i_tts.mp3',
            cached_until=timezone.now() + timedelta(days=30)
        )
        
        # Get audio
        audio = self.service.get_audio_for_phoneme(self.phoneme1, prefer_native=True)
        
        # Should prefer native
        self.assertEqual(audio.id, native.id)
    
    def test_expired_tts_not_returned(self):
        """Test that expired TTS audio is not returned."""
        # Create expired TTS
        expired_tts = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='tts',
            audio_file='phonemes/audio/i_tts_old.mp3',
            cached_until=timezone.now() - timedelta(days=1)  # Expired
        )
        
        # Get audio
        audio = self.service.get_audio_for_phoneme(self.phoneme1)
        
        # Should return None (expired not valid)
        self.assertIsNone(audio)
    
    def test_preferred_audio_source(self):
        """Test that preferred audio is used first."""
        # Create multiple audio sources
        native1 = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native1.mp3'
        )
        
        native2 = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native2.mp3'
        )
        
        # Set native2 as preferred
        self.phoneme1.preferred_audio_source = native2
        self.phoneme1.save()
        
        # Get audio
        audio = self.service.get_audio_for_phoneme(self.phoneme1)
        
        # Should return preferred (native2)
        self.assertEqual(audio.id, native2.id)
    
    def test_cache_hit(self):
        """Test that cache is used on second call."""
        # Create audio
        native = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # First call (cache miss)
        audio1 = self.service.get_audio_for_phoneme(self.phoneme1, use_cache=True)
        self.assertIsNotNone(audio1)
        self.assertEqual(audio1.id, native.id)
        
        # Second call (should use cache) - don't delete audio
        # Just verify cache key exists
        cache_key = self.service._get_cache_key(self.phoneme1.id)
        cached_id = cache.get(cache_key)
        self.assertIsNotNone(cached_id)
        self.assertEqual(cached_id, native.id)
    
    def test_cache_disabled(self):
        """Test with cache disabled."""
        # Create audio
        AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # Get audio without cache
        audio = self.service.get_audio_for_phoneme(self.phoneme1, use_cache=False)
        
        self.assertIsNotNone(audio)
    
    def test_usage_count_incremented(self):
        """Test that usage count is incremented on access."""
        # Create audio
        audio_src = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # Create cache
        cache_obj = AudioCache.objects.create(
            audio_source=audio_src,
            usage_count=5
        )
        
        # Get audio (should increment usage)
        self.service.get_audio_for_phoneme(self.phoneme1, use_cache=False)
        
        # Check usage count
        cache_obj.refresh_from_db()
        self.assertEqual(cache_obj.usage_count, 6)
    
    def test_get_audio_url(self):
        """Test getting audio URL."""
        # Create audio
        AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # Get URL
        url = self.service.get_audio_url(self.phoneme1)
        
        self.assertIsNotNone(url)
        self.assertIn('phonemes/audio/i_native.mp3', url)
    
    def test_get_audio_url_no_audio(self):
        """Test getting URL when no audio exists."""
        # Get URL
        url = self.service.get_audio_url(self.phoneme1)
        
        self.assertIsNone(url)
    
    def test_bulk_get_audio(self):
        """Test bulk audio retrieval."""
        # Create audio for multiple phonemes
        AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        AudioSource.objects.create(
            phoneme=self.phoneme2,
            source_type='tts',
            audio_file='phonemes/audio/i_short_tts.mp3',
            cached_until=timezone.now() + timedelta(days=30)
        )
        
        # No audio for phoneme3
        
        # Get audio for all phonemes
        phonemes = [self.phoneme1, self.phoneme2, self.phoneme3]
        audio_map = self.service.get_audio_for_phonemes_bulk(phonemes)
        
        # Check results
        self.assertEqual(len(audio_map), 3)
        self.assertIsNotNone(audio_map[self.phoneme1.id])
        self.assertIsNotNone(audio_map[self.phoneme2.id])
        self.assertIsNone(audio_map[self.phoneme3.id])
    
    def test_get_missing_audio_phonemes(self):
        """Test finding phonemes without audio."""
        # Create audio only for phoneme1
        AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # Get missing phonemes
        missing = self.service.get_missing_audio_phonemes()
        
        # Should return phoneme2 and phoneme3
        self.assertEqual(len(missing), 2)
        missing_ids = [p.id for p in missing]
        self.assertIn(self.phoneme2.id, missing_ids)
        self.assertIn(self.phoneme3.id, missing_ids)
        self.assertNotIn(self.phoneme1.id, missing_ids)
    
    def test_set_preferred_audio(self):
        """Test setting preferred audio."""
        # Create multiple audio sources
        native = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # Set as preferred
        success = self.service.set_preferred_audio(self.phoneme1, native)
        
        self.assertTrue(success)
        
        # Verify
        self.phoneme1.refresh_from_db()
        self.assertEqual(self.phoneme1.preferred_audio_source, native)
    
    def test_set_preferred_audio_wrong_phoneme(self):
        """Test setting preferred audio with wrong phoneme."""
        # Create audio for phoneme1
        audio = AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # Try to set as preferred for phoneme2 (should fail)
        success = self.service.set_preferred_audio(self.phoneme2, audio)
        
        self.assertFalse(success)
    
    def test_clear_cache_for_phoneme(self):
        """Test clearing cache for specific phoneme."""
        # Create audio
        AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        # Get audio to populate cache
        self.service.get_audio_for_phoneme(self.phoneme1, use_cache=True)
        
        # Clear cache
        success = self.service.clear_cache_for_phoneme(self.phoneme1.id)
        self.assertTrue(success)
        
        # Cache should be empty now
        cache_key = self.service._get_cache_key(self.phoneme1.id)
        self.assertIsNone(cache.get(cache_key))
    
    def test_audio_quality_report(self):
        """Test audio quality report generation."""
        # Create audio sources
        AudioSource.objects.create(
            phoneme=self.phoneme1,
            source_type='native',
            audio_file='phonemes/audio/i_native.mp3'
        )
        
        AudioSource.objects.create(
            phoneme=self.phoneme2,
            source_type='tts',
            audio_file='phonemes/audio/i_short_tts.mp3',
            cached_until=timezone.now() + timedelta(days=30)
        )
        
        # phoneme3 has no audio
        
        # Get report
        report = self.service.get_audio_quality_report()
        
        # Check report structure
        self.assertIn('total_phonemes', report)
        self.assertIn('phonemes_with_audio', report)
        self.assertIn('phonemes_without_audio', report)
        self.assertIn('coverage_percent', report)
        self.assertIn('native_audio_count', report)
        self.assertIn('tts_audio_count', report)
        self.assertIn('avg_quality_score', report)
        self.assertIn('by_category', report)
        
        # Check values
        self.assertEqual(report['total_phonemes'], 3)
        self.assertEqual(report['phonemes_with_audio'], 2)
        self.assertEqual(report['phonemes_without_audio'], 1)
        self.assertEqual(report['native_audio_count'], 1)
        self.assertEqual(report['tts_audio_count'], 1)
        
        # Coverage should be ~66.7%
        self.assertGreater(report['coverage_percent'], 65)
        self.assertLess(report['coverage_percent'], 68)


class PhonemeAudioServiceVoiceFilterTestCase(TestCase):
    """Test voice_id filtering in PhonemeAudioService."""
    
    def setUp(self):
        """Create test fixtures."""
        cache.clear()
        self.service = PhonemeAudioService()
        
        category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            category_type='vowel',
            order=1
        )
        
        self.phoneme = Phoneme.objects.create(
            category=category,
            ipa_symbol='i:',
            vietnamese_approx='vé kéo dài',
            order=1
        )
    
    def test_get_audio_with_voice_filter(self):
        """Test getting audio with specific voice_id."""
        # Create audio with different voices
        aria = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            voice_id='en-US-AriaNeural',
            audio_file='phonemes/audio/i_aria.mp3'
        )
        
        guy = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            voice_id='en-US-GuyNeural',
            audio_file='phonemes/audio/i_guy.mp3'
        )
        
        # Get Aria's voice
        audio_aria = self.service.get_audio_for_phoneme(
            self.phoneme,
            voice_id='en-US-AriaNeural'
        )
        
        self.assertIsNotNone(audio_aria)
        self.assertEqual(audio_aria.voice_id, 'en-US-AriaNeural')
        
        # Get Guy's voice
        audio_guy = self.service.get_audio_for_phoneme(
            self.phoneme,
            voice_id='en-US-GuyNeural'
        )
        
        self.assertIsNotNone(audio_guy)
        self.assertEqual(audio_guy.voice_id, 'en-US-GuyNeural')
    
    def test_voice_filter_no_match(self):
        """Test voice filter with no matching audio."""
        # Create audio with Aria voice
        AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            voice_id='en-US-AriaNeural',
            audio_file='phonemes/audio/i_aria.mp3'
        )
        
        # Try to get Jenny's voice (doesn't exist)
        audio = self.service.get_audio_for_phoneme(
            self.phoneme,
            voice_id='en-US-JennyNeural'
        )
        
        # Should return None
        self.assertIsNone(audio)
