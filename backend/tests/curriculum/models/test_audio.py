"""
Unit tests for AudioSource and AudioCache models.

Tests:
- Model creation and validation
- is_native() and is_cached() methods
- Quality scoring
- Cache age calculation
- Relationships with Phoneme
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.curriculum.models import (
    Phoneme,
    PhonemeCategory,
    AudioSource,
    AudioCache,
)


class AudioSourceModelTestCase(TestCase):
    """Test AudioSource model functionality."""
    
    def setUp(self):
        """Create test fixtures."""
        # Create phoneme category
        self.category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            category_type='vowel',
            order=1
        )
        
        # Create phoneme
        self.phoneme = Phoneme.objects.create(
            category=self.category,
            ipa_symbol='i:',
            vietnamese_approx='vé kéo dài',
            pronunciation_tips_vi='Nguyên âm dài i:',
            order=1
        )
    
    def test_create_native_audio(self):
        """Test creating native speaker audio source."""
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='phonemes/audio/2025/12/15/i_native.mp3',
            audio_duration=1.5
        )
        
        self.assertEqual(audio.phoneme, self.phoneme)
        self.assertEqual(audio.source_type, 'native')
        self.assertTrue(audio.is_native())
        self.assertEqual(audio.get_quality_score(), 100)
        self.assertTrue(audio.is_cached())  # Native never expires
        self.assertIsNotNone(audio.get_url())
    
    def test_create_tts_audio_cached(self):
        """Test creating cached TTS audio."""
        future_time = timezone.now() + timedelta(days=30)
        
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='tts',
            voice_id='en-US-AriaNeural',
            language='en-US',
            audio_file='phonemes/audio/2025/12/15/i_tts.mp3',
            audio_duration=1.2,
            cached_until=future_time
        )
        
        self.assertEqual(audio.source_type, 'tts')
        self.assertFalse(audio.is_native())
        self.assertEqual(audio.get_quality_score(), 90)
        self.assertTrue(audio.is_cached())  # Not expired
        self.assertFalse(audio.needs_regeneration())
    
    def test_expired_tts_audio(self):
        """Test that expired TTS audio is detected."""
        past_time = timezone.now() - timedelta(days=1)
        
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='tts',
            audio_file='phonemes/audio/2025/12/15/i_tts.mp3',
            cached_until=past_time
        )
        
        self.assertFalse(audio.is_cached())  # Expired
        self.assertTrue(audio.needs_regeneration())
    
    def test_generated_audio_quality(self):
        """Test on-demand generated audio."""
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='generated',
            audio_file='phonemes/audio/2025/12/15/i_generated.mp3'
        )
        
        self.assertEqual(audio.get_quality_score(), 80)
        self.assertFalse(audio.is_native())
    
    def test_multiple_audio_sources(self):
        """Test phoneme with multiple audio sources."""
        # Create native
        native = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='phonemes/audio/native.mp3'
        )
        
        # Create TTS
        tts = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='tts',
            audio_file='phonemes/audio/tts.mp3',
            cached_until=timezone.now() + timedelta(days=30)
        )
        
        # Check relationships
        audio_sources = self.phoneme.audio_sources.all()
        self.assertEqual(audio_sources.count(), 2)
        
        # Check they both exist (order doesn't matter for this test)
        audio_ids = [a.id for a in audio_sources]
        self.assertIn(native.id, audio_ids)
        self.assertIn(tts.id, audio_ids)
    
    def test_str_representation(self):
        """Test string representation."""
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='test.mp3'
        )
        
        expected = f"/{self.phoneme.ipa_symbol}/ - Native Speaker Recording"
        self.assertEqual(str(audio), expected)
    
    def test_metadata_json_field(self):
        """Test metadata JSON field."""
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='tts',
            audio_file='test.mp3',
            metadata={
                'tts_rate': '-30%',
                'quality': 'high',
                'speaker': 'Aria'
            }
        )
        
        self.assertEqual(audio.metadata['tts_rate'], '-30%')
        self.assertEqual(audio.metadata['quality'], 'high')
        self.assertEqual(audio.metadata['speaker'], 'Aria')


class AudioCacheModelTestCase(TestCase):
    """Test AudioCache model functionality."""
    
    def setUp(self):
        """Create test fixtures."""
        # Create phoneme
        category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            category_type='vowel',
            order=1
        )
        
        phoneme = Phoneme.objects.create(
            category=category,
            ipa_symbol='æ',
            vietnamese_approx='ê (ngắn)',
            pronunciation_tips_vi='Nguyên âm æ',
            order=1
        )
        
        # Create audio source
        self.audio = AudioSource.objects.create(
            phoneme=phoneme,
            source_type='tts',
            audio_file='phonemes/audio/test.mp3'
        )
    
    def test_create_cache(self):
        """Test creating audio cache."""
        cache = AudioCache.objects.create(
            audio_source=self.audio,
            file_size=1024 * 50,  # 50 KB
            usage_count=0
        )
        
        self.assertEqual(cache.audio_source, self.audio)
        self.assertEqual(cache.file_size, 51200)
        self.assertEqual(cache.usage_count, 0)
        self.assertIsNotNone(cache.generated_at)
    
    def test_increment_usage(self):
        """Test incrementing usage count."""
        cache = AudioCache.objects.create(
            audio_source=self.audio,
            usage_count=5
        )
        
        # Increment
        cache.increment_usage()
        cache.refresh_from_db()
        
        self.assertEqual(cache.usage_count, 6)
        
        # Increment again
        cache.increment_usage()
        cache.refresh_from_db()
        
        self.assertEqual(cache.usage_count, 7)
    
    def test_get_age_days(self):
        """Test calculating cache age."""
        cache = AudioCache.objects.create(
            audio_source=self.audio
        )
        
        age = cache.get_age_days()
        self.assertEqual(age, 0)  # Just created
    
    def test_is_stale(self):
        """Test cache staleness detection."""
        cache = AudioCache.objects.create(
            audio_source=self.audio
        )
        
        # Fresh cache
        self.assertFalse(cache.is_stale(max_days=30))
        
        # Simulate old cache by modifying generated_at
        cache.generated_at = timezone.now() - timedelta(days=35)
        cache.save()
        
        # Now it's stale
        self.assertTrue(cache.is_stale(max_days=30))
    
    def test_one_to_one_relationship(self):
        """Test one-to-one relationship with AudioSource."""
        cache = AudioCache.objects.create(
            audio_source=self.audio
        )
        
        # Access from AudioSource
        self.assertEqual(self.audio.cache, cache)
        
        # Access from AudioCache
        self.assertEqual(cache.audio_source, self.audio)
    
    def test_auto_timestamps(self):
        """Test automatic timestamp fields."""
        cache = AudioCache.objects.create(
            audio_source=self.audio
        )
        
        self.assertIsNotNone(cache.generated_at)
        self.assertIsNotNone(cache.last_accessed_at)
        
        # Wait a tiny bit and update
        import time
        time.sleep(0.01)  # 10ms wait
        
        # Update should change last_accessed_at
        old_time = cache.last_accessed_at
        cache.increment_usage()
        cache.refresh_from_db()
        
        # last_accessed_at should be updated (even if just slightly)
        self.assertGreaterEqual(cache.last_accessed_at, old_time)


class PhonemeAudioRelationTestCase(TestCase):
    """Test Phoneme-AudioSource relationships."""
    
    def setUp(self):
        """Create test fixtures."""
        category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            category_type='vowel',
            order=1
        )
        
        self.phoneme = Phoneme.objects.create(
            category=category,
            ipa_symbol='ʌ',
            vietnamese_approx='a (ngắn)',
            pronunciation_tips_vi='Nguyên âm ʌ',
            order=1
        )
    
    def test_preferred_audio_source(self):
        """Test setting preferred audio source."""
        # Create native audio
        native = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='native.mp3'
        )
        
        # Set as preferred
        self.phoneme.preferred_audio_source = native
        self.phoneme.save()
        
        # Verify
        self.phoneme.refresh_from_db()
        self.assertEqual(self.phoneme.preferred_audio_source, native)
    
    def test_preferred_audio_null(self):
        """Test phoneme without preferred audio."""
        self.assertIsNone(self.phoneme.preferred_audio_source)
    
    def test_cascade_delete(self):
        """Test cascading delete when phoneme is deleted."""
        # Create audio sources
        AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='native.mp3'
        )
        
        AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='tts',
            audio_file='tts.mp3'
        )
        
        # Should have 2 audio sources
        self.assertEqual(self.phoneme.audio_sources.count(), 2)
        
        # Delete phoneme
        phoneme_id = self.phoneme.id
        self.phoneme.delete()
        
        # Audio sources should be deleted too
        remaining_audio = AudioSource.objects.filter(phoneme_id=phoneme_id)
        self.assertEqual(remaining_audio.count(), 0)
    
    def test_set_null_on_audio_delete(self):
        """Test SET_NULL when preferred audio is deleted."""
        # Create audio
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='native.mp3'
        )
        
        # Set as preferred
        self.phoneme.preferred_audio_source = audio
        self.phoneme.save()
        
        # Delete audio
        audio.delete()
        
        # Phoneme should still exist with null preferred_audio_source
        self.phoneme.refresh_from_db()
        self.assertIsNone(self.phoneme.preferred_audio_source)
