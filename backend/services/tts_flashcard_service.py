"""
Flashcard Text-to-Speech Service

Provides audio generation for flashcard words using Edge-TTS with:
- Multiple voice options (US/UK, male/female)
- Speed control (slow/normal/fast)
- Redis caching (30-day TTL)
- Async generation with Celery
- Fallback to synchronous generation

Voice Options:
- en-US-GuyNeural (US Male)
- en-US-JennyNeural (US Female)
- en-GB-RyanNeural (UK Male)
- en-GB-SoniaNeural (UK Female)

Usage:
    from services.tts_flashcard_service import FlashcardTTSService
    
    service = FlashcardTTSService()
    audio_path = service.generate_audio(
        word="hello",
        voice="en-US-GuyNeural",
        speed="normal"
    )
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Literal
from django.conf import settings
from django.core.cache import cache
import edge_tts

logger = logging.getLogger(__name__)


class FlashcardTTSService:
    """
    Service for generating and managing TTS audio for flashcards.
    """
    
    # Voice configurations
    VOICES = {
        'us_male': 'en-US-GuyNeural',
        'us_female': 'en-US-JennyNeural',
        'uk_male': 'en-GB-RyanNeural',
        'uk_female': 'en-GB-SoniaNeural',
    }
    
    # Speed configurations (rate parameter for Edge-TTS)
    SPEEDS = {
        'slow': '-30%',      # 70% of normal speed
        'normal': '+0%',     # 100% normal speed
        'fast': '+20%',      # 120% speed
    }
    
    # Cache TTL (30 days)
    CACHE_TTL = 60 * 60 * 24 * 30
    
    def __init__(self):
        """Initialize TTS service."""
        # Audio storage directory
        self.audio_dir = Path(settings.MEDIA_ROOT) / 'flashcard_audio'
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Default voice
        self.default_voice = self.VOICES['us_male']
        self.default_speed = self.SPEEDS['normal']
    
    def get_cache_key(self, word: str, voice: str, speed: str) -> str:
        """
        Generate cache key for audio file.
        
        Args:
            word: The word to speak
            voice: Voice identifier
            speed: Speed identifier
            
        Returns:
            Cache key string
        """
        return f"flashcard_audio:{word.lower()}:{voice}:{speed}"
    
    def get_audio_filename(self, word: str, voice: str, speed: str) -> str:
        """
        Generate filename for audio file.
        
        Args:
            word: The word to speak
            voice: Voice identifier
            speed: Speed identifier
            
        Returns:
            Filename string (e.g., "hello_us_male_normal.mp3")
        """
        # Get voice shorthand
        voice_key = next(
            (k for k, v in self.VOICES.items() if v == voice),
            'us_male'
        )
        return f"{word.lower()}_{voice_key}_{speed}.mp3"
    
    def get_audio_path(self, word: str, voice: str, speed: str) -> Path:
        """
        Get full path to audio file.
        
        Args:
            word: The word to speak
            voice: Voice identifier
            speed: Speed identifier
            
        Returns:
            Path object
        """
        filename = self.get_audio_filename(word, voice, speed)
        return self.audio_dir / filename
    
    def get_audio_url(self, word: str, voice: str = None, speed: str = 'normal') -> Optional[str]:
        """
        Get URL for audio file (relative to MEDIA_URL).
        
        Args:
            word: The word to speak
            voice: Voice identifier (default: us_male)
            speed: Speed identifier (default: normal)
            
        Returns:
            URL string or None if not exists
        """
        voice = voice or self.default_voice
        audio_path = self.get_audio_path(word, voice, speed)
        
        if audio_path.exists():
            # Return relative URL
            relative_path = audio_path.relative_to(settings.MEDIA_ROOT)
            return f"{settings.MEDIA_URL}{relative_path}".replace('\\', '/')
        
        return None
    
    async def _generate_audio_async(
        self,
        word: str,
        voice: str,
        speed: str,
        output_path: Path
    ) -> bool:
        """
        Generate audio file using Edge-TTS (async).
        
        Args:
            word: The word to speak
            voice: Edge-TTS voice name
            speed: Speed rate string
            output_path: Path to save audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create TTS communicate object
            communicate = edge_tts.Communicate(
                text=word,
                voice=voice,
                rate=speed
            )
            
            # Generate and save audio
            await communicate.save(str(output_path))
            
            logger.info(f"Generated audio for '{word}' with voice '{voice}' at '{output_path}'")
            return True
            
        except Exception as e:
            logger.error(f"Error generating audio for '{word}': {e}")
            return False
    
    def generate_audio(
        self,
        word: str,
        voice: str = None,
        speed: Literal['slow', 'normal', 'fast'] = 'normal',
        force_regenerate: bool = False
    ) -> Optional[str]:
        """
        Generate audio for a word (synchronous wrapper).
        
        Args:
            word: The word to speak
            voice: Voice identifier (us_male, us_female, uk_male, uk_female)
            speed: Speed identifier (slow, normal, fast)
            force_regenerate: Force regeneration even if cached
            
        Returns:
            URL to audio file or None if failed
        """
        # Validate inputs
        voice = voice or 'us_male'
        if voice not in self.VOICES:
            logger.warning(f"Invalid voice '{voice}', using default")
            voice = 'us_male'
        
        if speed not in self.SPEEDS:
            logger.warning(f"Invalid speed '{speed}', using normal")
            speed = 'normal'
        
        # Get voice and speed codes
        voice_code = self.VOICES[voice]
        speed_rate = self.SPEEDS[speed]
        
        # Check cache first
        cache_key = self.get_cache_key(word, voice, speed)
        if not force_regenerate:
            cached_url = cache.get(cache_key)
            if cached_url:
                logger.debug(f"Audio for '{word}' found in cache")
                return cached_url
        
        # Check if file already exists
        audio_path = self.get_audio_path(word, voice_code, speed)
        if audio_path.exists() and not force_regenerate:
            url = self.get_audio_url(word, voice_code, speed)
            # Cache the URL
            cache.set(cache_key, url, self.CACHE_TTL)
            return url
        
        # Generate new audio
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                self._generate_audio_async(word, voice_code, speed_rate, audio_path)
            )
            loop.close()
            
            if success:
                url = self.get_audio_url(word, voice_code, speed)
                # Cache the URL
                cache.set(cache_key, url, self.CACHE_TTL)
                return url
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate audio for '{word}': {e}")
            return None
    
    def generate_multiple_audio(
        self,
        words: list[str],
        voice: str = None,
        speed: str = 'normal'
    ) -> dict[str, Optional[str]]:
        """
        Generate audio for multiple words.
        
        Args:
            words: List of words
            voice: Voice identifier
            speed: Speed identifier
            
        Returns:
            Dictionary mapping word to audio URL
        """
        results = {}
        for word in words:
            url = self.generate_audio(word, voice, speed)
            results[word] = url
        
        return results
    
    def delete_audio(self, word: str, voice: str = None, speed: str = 'normal') -> bool:
        """
        Delete audio file and cache entry.
        
        Args:
            word: The word
            voice: Voice identifier
            speed: Speed identifier
            
        Returns:
            True if deleted, False if not found
        """
        voice = voice or self.default_voice
        
        # Delete file
        audio_path = self.get_audio_path(word, voice, speed)
        if audio_path.exists():
            audio_path.unlink()
            logger.info(f"Deleted audio file: {audio_path}")
        
        # Delete cache
        cache_key = self.get_cache_key(word, voice, speed)
        cache.delete(cache_key)
        
        return True
    
    def get_available_voices(self) -> dict:
        """
        Get list of available voices.
        
        Returns:
            Dictionary of voice configurations
        """
        return {
            'voices': [
                {'id': 'us_male', 'name': 'US Male', 'code': self.VOICES['us_male']},
                {'id': 'us_female', 'name': 'US Female', 'code': self.VOICES['us_female']},
                {'id': 'uk_male', 'name': 'UK Male', 'code': self.VOICES['uk_male']},
                {'id': 'uk_female', 'name': 'UK Female', 'code': self.VOICES['uk_female']},
            ],
            'speeds': [
                {'id': 'slow', 'name': 'Slow (70%)', 'rate': self.SPEEDS['slow']},
                {'id': 'normal', 'name': 'Normal', 'rate': self.SPEEDS['normal']},
                {'id': 'fast', 'name': 'Fast (120%)', 'rate': self.SPEEDS['fast']},
            ]
        }
    
    def get_storage_stats(self) -> dict:
        """
        Get audio storage statistics.
        
        Returns:
            Dictionary with storage info
        """
        audio_files = list(self.audio_dir.glob('*.mp3'))
        total_size = sum(f.stat().st_size for f in audio_files)
        
        return {
            'total_files': len(audio_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'storage_path': str(self.audio_dir),
        }


# Singleton instance
_tts_service = None

def get_tts_service() -> FlashcardTTSService:
    """
    Get singleton TTS service instance.
    
    Returns:
        FlashcardTTSService instance
    """
    global _tts_service
    if _tts_service is None:
        _tts_service = FlashcardTTSService()
    return _tts_service
