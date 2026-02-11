"""
Text-to-Speech Service using Edge TTS (Microsoft Neural Voices).

This module provides high-quality neural TTS for pronunciation learning.
Edge TTS is free and uses Microsoft Azure Neural voices.

Usage:
    from utils.tts import TTSService
    
    # Synchronous
    audio_path = TTSService.speak("Hello world", voice="en-US-AriaNeural")
    
    # Asynchronous  
    audio_path = await TTSService.speak_async("Hello world")

Available voices for English:
    - en-US-AriaNeural (Female, US)
    - en-US-GuyNeural (Male, US)
    - en-US-JennyNeural (Female, US)
    - en-GB-SoniaNeural (Female, UK)
    - en-GB-RyanNeural (Male, UK)
    - en-AU-NatashaNeural (Female, AU)
"""

import os
import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import edge_tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts not installed. Run: pip install edge-tts")


class TTSVoice:
    """Available TTS voices for different accents."""
    
    # American English
    US_FEMALE_ARIA = "en-US-AriaNeural"
    US_FEMALE_JENNY = "en-US-JennyNeural"
    US_MALE_GUY = "en-US-GuyNeural"
    US_MALE_DAVIS = "en-US-DavisNeural"
    
    # British English
    UK_FEMALE_SONIA = "en-GB-SoniaNeural"
    UK_FEMALE_LIBBY = "en-GB-LibbyNeural"
    UK_MALE_RYAN = "en-GB-RyanNeural"
    UK_MALE_THOMAS = "en-GB-ThomasNeural"
    
    # Australian English
    AU_FEMALE_NATASHA = "en-AU-NatashaNeural"
    AU_MALE_WILLIAM = "en-AU-WilliamNeural"
    
    # Default voice
    DEFAULT = US_FEMALE_ARIA
    
    @classmethod
    def get_all(cls):
        """Get all available voices."""
        return {
            'us': {
                'female': [cls.US_FEMALE_ARIA, cls.US_FEMALE_JENNY],
                'male': [cls.US_MALE_GUY, cls.US_MALE_DAVIS]
            },
            'uk': {
                'female': [cls.UK_FEMALE_SONIA, cls.UK_FEMALE_LIBBY],
                'male': [cls.UK_MALE_RYAN, cls.UK_MALE_THOMAS]
            },
            'au': {
                'female': [cls.AU_FEMALE_NATASHA],
                'male': [cls.AU_MALE_WILLIAM]
            }
        }


class TTSService:
    """
    Text-to-Speech service using Edge TTS.
    
    Features:
    - High-quality Microsoft Neural voices (free)
    - Multiple accents: US, UK, AU
    - Audio caching to avoid regenerating same text
    - Async and sync support
    - Rate and pitch control
    """
    
    # Audio output directory
    AUDIO_DIR = Path(settings.MEDIA_ROOT) / 'tts'
    
    # Default settings
    DEFAULT_VOICE = TTSVoice.DEFAULT
    DEFAULT_RATE = "+0%"  # Speed: -50% to +100%
    DEFAULT_PITCH = "+0Hz"  # Pitch: -50Hz to +50Hz
    
    @classmethod
    def _get_cache_path(cls, text: str, voice: str, rate: str, pitch: str) -> Path:
        """Generate cache file path based on text and settings hash."""
        # Create hash of text + settings for caching
        cache_key = f"{text}_{voice}_{rate}_{pitch}"
        file_hash = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Organize by voice
        voice_dir = cls.AUDIO_DIR / voice
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        return voice_dir / f"{file_hash}.mp3"
    
    @classmethod
    async def speak_async(
        cls,
        text: str,
        voice: str = None,
        rate: str = None,
        pitch: str = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Generate speech audio asynchronously.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (default: en-US-AriaNeural)
            rate: Speech rate (e.g., "+10%", "-20%")
            pitch: Voice pitch (e.g., "+5Hz", "-10Hz")
            use_cache: Whether to use cached audio if available
            
        Returns:
            Path to generated MP3 file, or None if failed
        """
        if not EDGE_TTS_AVAILABLE:
            logger.error("edge-tts not available")
            return None
        
        if not text or not text.strip():
            return None
        
        # Use defaults
        voice = voice or cls.DEFAULT_VOICE
        rate = rate or cls.DEFAULT_RATE
        pitch = pitch or cls.DEFAULT_PITCH
        
        # Check cache
        cache_path = cls._get_cache_path(text, voice, rate, pitch)
        
        if use_cache and cache_path.exists():
            logger.debug(f"Using cached audio: {cache_path}")
            return str(cache_path)
        
        try:
            # Generate audio
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch
            )
            
            await communicate.save(str(cache_path))
            logger.info(f"Generated TTS audio: {cache_path}")
            
            return str(cache_path)
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    @classmethod
    def speak(
        cls,
        text: str,
        voice: str = None,
        rate: str = None,
        pitch: str = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Generate speech audio synchronously.
        
        This is a wrapper around speak_async for synchronous code.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            cls.speak_async(text, voice, rate, pitch, use_cache)
        )
    
    @classmethod
    async def speak_phoneme_async(
        cls,
        ipa_symbol: str,
        example_word: str = None,
        voice: str = None
    ) -> dict:
        """
        Generate audio for IPA phoneme practice.
        
        Returns dict with paths to:
        - phoneme_audio: Just the sound (e.g., "ah")
        - word_audio: Example word (e.g., "father")
        - slow_audio: Slow pronunciation
        """
        voice = voice or cls.DEFAULT_VOICE
        result = {}
        
        # Map IPA to pronounceable text
        ipa_to_text = {
            'ɪ': 'ih',
            'e': 'eh',
            'æ': 'ah',
            'ʌ': 'uh',
            'ʊ': 'oo',
            'ɒ': 'o',
            'ə': 'uh',
            'iː': 'ee',
            'uː': 'oo',
            'ɜː': 'er',
            'ɔː': 'aw',
            'ɑː': 'ah',
            'eɪ': 'ay',
            'aɪ': 'eye',
            'ɔɪ': 'oy',
            'aʊ': 'ow',
            'əʊ': 'oh',
            'ɪə': 'ear',
            'eə': 'air',
            'ʊə': 'oor',
            'p': 'p',
            't': 't',
            'k': 'k',
            'f': 'f',
            'θ': 'th',
            's': 's',
            'ʃ': 'sh',
            'tʃ': 'ch',
            'h': 'h',
            'b': 'b',
            'd': 'd',
            'g': 'g',
            'v': 'v',
            'ð': 'th',
            'z': 'z',
            'ʒ': 'zh',
            'dʒ': 'j',
            'm': 'm',
            'n': 'n',
            'ŋ': 'ng',
            'l': 'l',
            'r': 'r',
            'w': 'w',
            'j': 'y',
        }
        
        # Get pronounceable text
        phoneme_text = ipa_to_text.get(ipa_symbol, ipa_symbol)
        
        # Generate phoneme sound
        result['phoneme_audio'] = await cls.speak_async(
            phoneme_text, voice=voice
        )
        
        # Generate example word if provided
        if example_word:
            result['word_audio'] = await cls.speak_async(
                example_word, voice=voice
            )
            
            # Slow version
            result['slow_audio'] = await cls.speak_async(
                example_word, voice=voice, rate="-30%"
            )
        
        return result
    
    @classmethod
    async def speak_sentence_async(
        cls,
        sentence: str,
        voice: str = None,
        slow: bool = False
    ) -> Optional[str]:
        """
        Generate audio for a full sentence.
        
        Args:
            sentence: Sentence to speak
            voice: Voice to use
            slow: Whether to speak slowly (for learners)
        """
        rate = "-25%" if slow else "+0%"
        return await cls.speak_async(sentence, voice=voice, rate=rate)
    
    @classmethod
    async def list_voices_async(cls) -> list:
        """Get list of all available voices."""
        if not EDGE_TTS_AVAILABLE:
            return []
        
        try:
            voices = await edge_tts.list_voices()
            # Filter English voices
            english_voices = [
                v for v in voices 
                if v['Locale'].startswith('en-')
            ]
            return english_voices
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []
    
    @classmethod
    def clear_cache(cls, voice: str = None) -> int:
        """
        Clear cached audio files.
        
        Args:
            voice: If provided, only clear cache for this voice
            
        Returns:
            Number of files deleted
        """
        count = 0
        
        if voice:
            voice_dir = cls.AUDIO_DIR / voice
            if voice_dir.exists():
                for f in voice_dir.glob("*.mp3"):
                    f.unlink()
                    count += 1
        else:
            if cls.AUDIO_DIR.exists():
                for f in cls.AUDIO_DIR.rglob("*.mp3"):
                    f.unlink()
                    count += 1
        
        logger.info(f"Cleared {count} cached audio files")
        return count


# Convenience function
def speak(text: str, voice: str = None) -> Optional[str]:
    """Quick function to generate speech."""
    return TTSService.speak(text, voice)
