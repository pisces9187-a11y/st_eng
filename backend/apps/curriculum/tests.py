"""Quick tests for PhonemeAudioService - Phase 1 Day 2."""

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache

from apps.curriculum.models import (
    PhonemeCategory, Phoneme, AudioSource, AudioCache
)
from apps.curriculum.services import PhonemeAudioService


class TestAudioSourceModel(TestCase):
    """Test AudioSource model methods."""
    
    def setUp(self):
        """Create test fixtures."""
        self.category = PhonemeCategory.objects.create(
            name='Short Vowels',
            name_vi='Nguyên âm ngắn',
            category_type='vowel',
            order=1
        )
        
        self.phoneme = Phoneme.objects.create(
            category=self.category,
            ipa_symbol='ɪ',
            vietnamese_approx='giống "i" trong "it"',
            phoneme_type='short_vowel',
            order=1
        )
    
    def test_create_native_audio_source(self):
        """Test creating native speaker audio source."""
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            voice_id='native-male-1',
            audio_file='test.mp3',
            audio_duration=1.5
        )
        
        self.assertEqual(audio.phoneme, self.phoneme)
        self.assertEqual(audio.source_type, 'native')
        self.assertTrue(audio.is_native())
        self.assertEqual(audio.get_quality_score(), 100)
    
    def test_create_tts_audio_source(self):
        """Test creating TTS audio source."""
        future_time = timezone.now() + timedelta(days=30)
        
        audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='tts',
            voice_id='en-US-AriaNeural',
            audio_file='tts.mp3',
            audio_duration=1.2,
            cached_until=future_time
        )
        
        self.assertEqual(audio.source_type, 'tts')
        self.assertFalse(audio.is_native())
        self.assertEqual(audio.get_quality_score(), 90)
        self.assertTrue(audio.is_cached())


class TestPhonemeAudioService(TestCase):
    """Test PhonemeAudioService business logic."""
    
    def setUp(self):
        """Create test fixtures."""
        cache.clear()
        
        self.category = PhonemeCategory.objects.create(
            name='Short Vowels',
            name_vi='Nguyên âm ngắn',
            category_type='vowel',
            order=1
        )
        
        self.phoneme = Phoneme.objects.create(
            category=self.category,
            ipa_symbol='ɪ',
            vietnamese_approx='i ngắn',
            phoneme_type='short_vowel',
            order=1
        )
        
        self.service = PhonemeAudioService()
    
    def tearDown(self):
        """Clean up after each test."""
        cache.clear()
    
    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = PhonemeAudioService()
        self.assertIsNotNone(service)
        self.assertTrue(service.cache_enabled)
    
    def test_get_audio_preferred(self):
        """Test getting audio from preferred_audio_source."""
        # Create native audio
        native_audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            voice_id='native-male',
            audio_file='native.mp3',
            audio_duration=1.5
        )
        
        # Create cache
        AudioCache.objects.create(
            audio_source=native_audio,
            usage_count=0
        )
        
        # Set as preferred
        self.phoneme.preferred_audio_source = native_audio
        self.phoneme.save()
        
        # Get audio
        result = self.service.get_audio_for_phoneme(self.phoneme)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, native_audio.id)
        self.assertEqual(result.source_type, 'native')
    
    def test_get_audio_fallback_to_native(self):
        """Test fallback to native audio when no preferred."""
        # Create native audio (no preferred set)
        native_audio = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='native.mp3'
        )
        AudioCache.objects.create(audio_source=native_audio)
        
        # Get audio
        result = self.service.get_audio_for_phoneme(self.phoneme)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.source_type, 'native')
    
    def test_get_audio_returns_none_when_no_audio(self):
        """Test returns None when no audio available."""
        result = self.service.get_audio_for_phoneme(self.phoneme)
        self.assertIsNone(result)
    
    def test_bulk_get_audio(self):
        """Test bulk audio retrieval."""
        # Create second phoneme
        phoneme2 = Phoneme.objects.create(
            category=self.category,
            ipa_symbol='e',
            phoneme_type='short_vowel',
            order=2
        )
        
        # Create audio for phoneme1
        audio1 = AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='audio1.mp3'
        )
        AudioCache.objects.create(audio_source=audio1)
        
        # Bulk get
        phonemes = [self.phoneme, phoneme2]
        results = self.service.get_audio_for_phonemes_bulk(phonemes)
        
        self.assertEqual(len(results), 2)
        self.assertIn(self.phoneme.id, results)
        self.assertIsNotNone(results[self.phoneme.id])
        self.assertIsNone(results[phoneme2.id])
    
    def test_get_audio_quality_report(self):
        """Test quality report generation."""
        # Create audio
        AudioSource.objects.create(
            phoneme=self.phoneme,
            source_type='native',
            audio_file='native.mp3'
        )
        
        report = self.service.get_audio_quality_report()
        
        self.assertIn('total_phonemes', report)
        self.assertIn('phonemes_with_audio', report)
        self.assertIn('coverage_percent', report)
        self.assertTrue(report['cache_enabled'])
