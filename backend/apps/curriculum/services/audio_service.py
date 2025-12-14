"""PhonemeAudioService: Smart audio retrieval with fallback logic.

This service implements intelligent audio source selection:
1. Check preferred audio (native > cached TTS)
2. Fallback to any native audio
3. Fallback to cached TTS
4. Return None for on-demand generation

Features:
- 4-tier fallback hierarchy
- Django cache integration
- Bulk operations
- Performance metrics
- Quality scoring
"""

import logging
from typing import Optional, Dict, List, Tuple
from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, Prefetch, Count, Avg
from django.utils import timezone
from ..models import PhonemeCategory
from apps.curriculum.models import Phoneme, AudioSource, AudioCache


logger = logging.getLogger(__name__)


class PhonemeAudioService:
    """
    Service for intelligent phoneme audio retrieval and management.
    
    Usage:
        >>> service = PhonemeAudioService()
        >>> audio = service.get_audio_for_phoneme(phoneme)
        >>> if audio:
        ...     print(f"Quality: {audio.get_quality_score()}%")
        ...     print(f"URL: {audio.get_url()}")
    
    Cache Keys:
        - phoneme_audio:{phoneme_id} -> AudioSource ID
        - phoneme_audio_url:{phoneme_id} -> Audio URL
    """
    
    # Cache TTL settings
    CACHE_TTL_PREFERRED = 3600  # 1 hour for preferred audio
    CACHE_TTL_FALLBACK = 1800   # 30 minutes for fallback
    CACHE_TTL_URL = 600         # 10 minutes for URLs
    
    # Quality thresholds
    MIN_QUALITY_SCORE = 80  # Minimum acceptable quality
    PREFER_NATIVE_THRESHOLD = 90  # Prefer native if available
    
    def __init__(self):
        """Initialize the audio service."""
        self.cache_enabled = self._check_cache_available()
        if not self.cache_enabled:
            logger.warning("Django cache not available - performance will be degraded")
    
    @staticmethod
    def _check_cache_available() -> bool:
        """Check if Django cache is configured and working."""
        try:
            cache.set('_test_key', 'test_value', 1)
            return cache.get('_test_key') == 'test_value'
        except Exception as e:
            logger.error(f"Cache check failed: {e}")
            return False
    
    # =========================================================================
    # PRIMARY API: Get Audio for Phoneme
    # =========================================================================
    
    def get_audio_for_phoneme(
        self,
        phoneme: Phoneme,
        voice_id: Optional[str] = None,
        prefer_native: bool = True,
        use_cache: bool = True
    ) -> Optional[AudioSource]:
        """
        Get the best available audio for a phoneme with smart fallback.
        
        Fallback hierarchy:
        1. Preferred audio (if set and valid)
        2. Native speaker audio (highest quality)
        3. Cached TTS audio (good quality, instant)
        4. None (trigger on-demand generation)
        
        Args:
            phoneme: Phoneme instance
            voice_id: Specific voice ID to use (optional)
            prefer_native: Prefer native over TTS even if lower usage
            use_cache: Use Django cache for faster retrieval
        
        Returns:
            AudioSource instance or None
        
        Example:
            >>> phoneme = Phoneme.objects.get(ipa_symbol='i:')
            >>> audio = service.get_audio_for_phoneme(phoneme)
            >>> if audio:
            ...     print(f"Found: {audio.source_type}")
            ... else:
            ...     print("Need to generate TTS")
        """
        # Try cache first
        if use_cache and self.cache_enabled:
            cached_audio = self._get_from_cache(phoneme.id, voice_id)
            if cached_audio:
                logger.debug(f"Cache HIT for phoneme {phoneme.id}")
                return cached_audio
            logger.debug(f"Cache MISS for phoneme {phoneme.id}")
        
        # Step 1: Check preferred audio
        if phoneme.preferred_audio_source:
            audio = phoneme.preferred_audio_source
            if self._is_audio_valid(audio, voice_id):
                logger.info(f"Using preferred audio for /{phoneme.ipa_symbol}/")
                self._increment_usage(audio)
                if use_cache:
                    self._save_to_cache(phoneme.id, audio, voice_id)
                return audio
        
        # Step 2: Try native audio
        if prefer_native:
            native_audio = self._get_native_audio(phoneme, voice_id)
            if native_audio:
                logger.info(f"Using native audio for /{phoneme.ipa_symbol}/")
                self._increment_usage(native_audio)
                if use_cache:
                    self._save_to_cache(phoneme.id, native_audio, voice_id)
                return native_audio
        
        # Step 3: Try cached TTS
        tts_audio = self._get_cached_tts(phoneme, voice_id)
        if tts_audio:
            logger.info(f"Using cached TTS for /{phoneme.ipa_symbol}/")
            self._increment_usage(tts_audio)
            if use_cache:
                self._save_to_cache(phoneme.id, tts_audio, voice_id)
            return tts_audio
        
        # Step 4: No audio available - need generation
        logger.warning(f"No audio available for /{phoneme.ipa_symbol}/ - needs generation")
        return None
    
    def get_audio_url(
        self,
        phoneme: Phoneme,
        voice_id: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Get audio URL for a phoneme (cached for performance).
        
        Args:
            phoneme: Phoneme instance
            voice_id: Specific voice ID (optional)
            use_cache: Use URL cache
        
        Returns:
            Audio file URL or None
        """
        # Try URL cache first
        if use_cache and self.cache_enabled:
            cache_key = self._get_url_cache_key(phoneme.id, voice_id)
            url = cache.get(cache_key)
            if url:
                return url
        
        # Get audio source
        audio = self.get_audio_for_phoneme(phoneme, voice_id, use_cache=use_cache)
        if not audio:
            return None
        
        url = audio.get_url()
        
        # Cache URL
        if use_cache and self.cache_enabled and url:
            cache_key = self._get_url_cache_key(phoneme.id, voice_id)
            cache.set(cache_key, url, self.CACHE_TTL_URL)
        
        return url
    
    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================
    
    def get_audio_for_phonemes_bulk(
        self,
        phonemes: List[Phoneme],
        voice_id: Optional[str] = None
    ) -> Dict[int, Optional[AudioSource]]:
        """
        Get audio for multiple phonemes efficiently (single query).
        
        Args:
            phonemes: List of Phoneme instances
            voice_id: Voice ID filter (optional)
        
        Returns:
            Dict mapping phoneme_id -> AudioSource (or None)
        
        Example:
            >>> phonemes = Phoneme.objects.filter(category__category_type='vowel')[:10]
            >>> audio_map = service.get_audio_for_phonemes_bulk(phonemes)
            >>> for phoneme in phonemes:
            ...     audio = audio_map.get(phoneme.id)
            ...     if audio:
            ...         print(f"/{phoneme.ipa_symbol}/: {audio.source_type}")
        """
        phoneme_ids = [p.id for p in phonemes]
        
        # Prefetch all audio sources in one query
        phonemes_with_audio = Phoneme.objects.filter(
            id__in=phoneme_ids
        ).prefetch_related(
            Prefetch(
                'audio_sources',
                queryset=AudioSource.objects.select_related('cache').order_by(
                    # Order by quality: native > tts > generated
                    '-source_type',  # 'native' > 'tts' > 'generated' alphabetically reversed
                )
            ),
            'preferred_audio_source'
        )
        
        result = {}
        for phoneme in phonemes_with_audio:
            audio = self._select_best_audio_from_prefetched(
                phoneme,
                voice_id
            )
            result[phoneme.id] = audio
            
            if audio:
                self._increment_usage(audio)
        
        return result
    
    def get_missing_audio_phonemes(
        self,
        category_type: Optional[str] = None
    ) -> List[Phoneme]:
        """
        Get phonemes that have no audio sources.
        
        Args:
            category_type: Filter by category type (vowel/consonant/diphthong)
        
        Returns:
            List of Phoneme instances without audio
        
        Example:
            >>> missing = service.get_missing_audio_phonemes(category_type='vowel')
            >>> print(f"Need to record {len(missing)} vowels")
        """
        queryset = Phoneme.objects.annotate(
            audio_count=Count('audio_sources')
        ).filter(audio_count=0)
        
        if category_type:
            queryset = queryset.filter(category__category_type=category_type)
        
        return list(queryset.select_related('category'))
    
    # =========================================================================
    # AUDIO QUALITY & METRICS
    # =========================================================================
    
    def get_audio_quality_report(self):
        """Get comprehensive audio quality and coverage report."""
        phonemes_qs = Phoneme.objects.all().select_related('category', 'preferred_audio_source')
        total_phonemes = phonemes_qs.count()
        
        phonemes_with_audio = 0
        native_count = 0
        tts_count = 0
        generated_count = 0
        total_quality = 0
        
        for phoneme in phonemes_qs:
            audio = self.get_audio_for_phoneme(phoneme)
            if audio:
                phonemes_with_audio += 1
                total_quality += audio.get_quality_score()
                
                if audio.source_type == 'native':
                    native_count += 1
                elif audio.source_type == 'tts':
                    tts_count += 1
                elif audio.source_type == 'generated':
                    generated_count += 1
        
        coverage_percent = (phonemes_with_audio / total_phonemes * 100) if total_phonemes > 0 else 0.0
        avg_quality_score = (total_quality / phonemes_with_audio) if phonemes_with_audio > 0 else 0.0
        
        by_category = {}
        categories = PhonemeCategory.objects.all().prefetch_related('phonemes')
        for category in categories:
            cat_phonemes = category.phonemes.all()
            cat_total = cat_phonemes.count()
            cat_with_audio = sum(1 for p in cat_phonemes if self.get_audio_for_phoneme(p))
            cat_coverage = (cat_with_audio / cat_total * 100) if cat_total > 0 else 0.0
            
            by_category[category.category_type] = {
                'total': cat_total,
                'with_audio': cat_with_audio,
                'coverage': round(cat_coverage, 1)
            }
        
        return {
            'total_phonemes': total_phonemes,
            'phonemes_with_audio': phonemes_with_audio,
            'phonemes_without_audio': total_phonemes - phonemes_with_audio,  # FIX
            'coverage_percent': round(coverage_percent, 1),
            'native_audio_count': native_count,
            'tts_audio_count': tts_count,
            'generated_audio_count': generated_count,  # FIX
            'avg_quality_score': round(avg_quality_score, 1),
            'cache_enabled': True,
            'by_category': by_category
        }


    def set_preferred_audio(
        self,
        phoneme: Phoneme,
        audio_source: AudioSource
    ) -> bool:
        """
        Set preferred audio source for a phoneme.
        
        Args:
            phoneme: Phoneme instance
            audio_source: AudioSource to set as preferred
        
        Returns:
            True if successful
        
        Example:
            >>> audio = AudioSource.objects.filter(
            ...     phoneme=phoneme,
            ...     source_type='native'
            ... ).first()
            >>> if audio:
            ...     service.set_preferred_audio(phoneme, audio)
        """
        if audio_source.phoneme_id != phoneme.id:
            logger.error(f"AudioSource {audio_source.id} does not belong to phoneme {phoneme.id}")
            return False
        
        phoneme.preferred_audio_source = audio_source
        phoneme.save(update_fields=['preferred_audio_source'])
        
        # Invalidate cache
        self._invalidate_cache(phoneme.id)
        
        logger.info(f"Set preferred audio for /{phoneme.ipa_symbol}/ to {audio_source.source_type}")
        return True
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    def clear_cache_for_phoneme(self, phoneme_id: int) -> bool:
        """
        Clear all cache entries for a specific phoneme.
        
        Args:
            phoneme_id: Phoneme ID
        
        Returns:
            True if successful
        """
        return self._invalidate_cache(phoneme_id)
    
    def clear_all_audio_cache(self) -> int:
        """
        Clear all audio-related cache entries.
        
        Returns:
            Number of cache entries cleared (approximate)
        """
        if not self.cache_enabled:
            return 0
        
        # This is a simplified implementation
        # In production, use cache.delete_many() with pattern matching
        count = 0
        phoneme_ids = Phoneme.objects.values_list('id', flat=True)
        for phoneme_id in phoneme_ids:
            if self._invalidate_cache(phoneme_id):
                count += 1
        
        logger.info(f"Cleared {count} audio cache entries")
        return count
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _get_native_audio(
        self,
        phoneme: Phoneme,
        voice_id: Optional[str] = None
    ) -> Optional[AudioSource]:
        """Get native speaker audio for phoneme."""
        queryset = AudioSource.objects.filter(
            phoneme=phoneme,
            source_type='native'
        ).select_related('cache')
        
        if voice_id:
            queryset = queryset.filter(voice_id=voice_id)
        
        # Order by usage (most used first)
        queryset = queryset.order_by('-cache__usage_count')
        
        return queryset.first()
    
    def _get_cached_tts(
        self,
        phoneme: Phoneme,
        voice_id: Optional[str] = None
    ) -> Optional[AudioSource]:
        """Get cached TTS audio for phoneme."""
        now = timezone.now()
        
        queryset = AudioSource.objects.filter(
            phoneme=phoneme,
            source_type='tts',
            cached_until__gt=now  # Not expired
        ).select_related('cache')
        
        if voice_id:
            queryset = queryset.filter(voice_id=voice_id)
        
        # Order by usage
        queryset = queryset.order_by('-cache__usage_count')
        
        return queryset.first()
    
    def _is_audio_valid(
        self,
        audio: AudioSource,
        voice_id: Optional[str] = None
    ) -> bool:
        """Check if audio source is valid and not expired."""
        # Check voice_id match
        if voice_id and audio.voice_id != voice_id:
            return False
        
        # Native audio never expires
        if audio.is_native():
            return True
        
        # Check TTS cache expiration
        return audio.is_cached()
    
    def _select_best_audio_from_prefetched(
        self,
        phoneme: Phoneme,
        voice_id: Optional[str] = None
    ) -> Optional[AudioSource]:
        """Select best audio from prefetched audio_sources."""
        # Check preferred first
        if phoneme.preferred_audio_source:
            if self._is_audio_valid(phoneme.preferred_audio_source, voice_id):
                return phoneme.preferred_audio_source
        
        # Check all audio sources (already ordered by quality)
        for audio in phoneme.audio_sources.all():
            if self._is_audio_valid(audio, voice_id):
                return audio
        
        return None
    
    def _increment_usage(self, audio: AudioSource) -> None:
        """Increment usage counter for audio source."""
        try:
            if hasattr(audio, 'cache'):
                audio.cache.increment_usage()
            else:
                # Create cache if not exists
                AudioCache.objects.create(
                    audio_source=audio,
                    usage_count=1
                )
        except Exception as e:
            logger.warning(f"Failed to increment usage for audio {audio.id}: {e}")
    
    # Cache key generators
    
    @staticmethod
    def _get_cache_key(phoneme_id: int, voice_id: Optional[str] = None) -> str:
        """Generate cache key for audio source."""
        if voice_id:
            return f"phoneme_audio:{phoneme_id}:{voice_id}"
        return f"phoneme_audio:{phoneme_id}"
    
    @staticmethod
    def _get_url_cache_key(phoneme_id: int, voice_id: Optional[str] = None) -> str:
        """Generate cache key for audio URL."""
        if voice_id:
            return f"phoneme_audio_url:{phoneme_id}:{voice_id}"
        return f"phoneme_audio_url:{phoneme_id}"
    
    def _get_from_cache(
        self,
        phoneme_id: int,
        voice_id: Optional[str] = None
    ) -> Optional[AudioSource]:
        """Get audio source from cache."""
        cache_key = self._get_cache_key(phoneme_id, voice_id)
        audio_id = cache.get(cache_key)
        
        if audio_id:
            try:
                return AudioSource.objects.select_related('cache').get(id=audio_id)
            except AudioSource.DoesNotExist:
                # Cache is stale, delete it
                cache.delete(cache_key)
        
        return None
    
    def _save_to_cache(
        self,
        phoneme_id: int,
        audio: AudioSource,
        voice_id: Optional[str] = None
    ) -> None:
        """Save audio source to cache."""
        cache_key = self._get_cache_key(phoneme_id, voice_id)
        ttl = self.CACHE_TTL_PREFERRED if audio.is_native() else self.CACHE_TTL_FALLBACK
        cache.set(cache_key, audio.id, ttl)
    
    def _invalidate_cache(self, phoneme_id: int) -> bool:
        """Invalidate all cache entries for a phoneme."""
        if not self.cache_enabled:
            return False
        
        # Delete both regular and voice-specific caches
        cache.delete(self._get_cache_key(phoneme_id))
        cache.delete(self._get_url_cache_key(phoneme_id))
        
        # Note: In production, also delete voice_id-specific caches
        # This would require tracking all voice_ids or using Redis pattern matching
        
        return True
