"""
Enhanced Edge TTS Service for English Learning Platform
Based on HUONG_DAN_TICH_HOP.md

Features:
- Multiple English voice variants (US, UK, AU, CA, IN)
- Speed adjustment based on student level
- Voice caching to avoid regeneration
- Flexible API for different use cases
- Mock mode support for offline development
"""

import edge_tts
import asyncio
import hashlib
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime

from django.conf import settings
from django.core.files import File
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_mock_tts_mode():
    """Check if mock TTS mode is enabled."""
    env_mock = os.environ.get('MOCK_TTS', '').lower()
    if env_mock in ('true', 'false'):
        return env_mock == 'true'
    return getattr(settings, 'MOCK_TTS_MODE', False)


class EnglishTTSService:
    """
    Enhanced TTS Service for English Learning Platform.
    
    Usage:
        >>> tts = EnglishTTSService()
        >>> # Generate word pronunciation
        >>> audio_path = await tts.generate_word_pronunciation("beautiful", accent="us")
        >>> 
        >>> # Generate sentence with speed adjustment
        >>> audio_path = await tts.generate_sentence_audio(
        ...     "The weather is nice today.",
        ...     student_level="beginner",
        ...     voice_type="female"
        ... )
    """
    
    # =========================================================================
    # VOICE CONFIGURATIONS
    # =========================================================================
    
    VOICES = {
        # Giọng Mỹ (American English) - Khuyên dùng cho học viên
        "us_female_clear": {
            "id": "en-US-AriaNeural",
            "gender": "female",
            "accent": "US",
            "description": "Giọng nữ Mỹ rõ ràng, tự nhiên - Tốt nhất cho học từ vựng",
            "recommended": True
        },
        "us_male_standard": {
            "id": "en-US-GuyNeural",
            "gender": "male",
            "accent": "US",
            "description": "Giọng nam Mỹ ấm, chuẩn - Phù hợp bài đọc",
            "recommended": True
        },
        "us_female_young": {
            "id": "en-US-JennyNeural",
            "gender": "female",
            "accent": "US",
            "description": "Giọng nữ trẻ trung, năng động - Cho học sinh, thanh thiếu niên",
            "recommended": False
        },
        "us_male_professional": {
            "id": "en-US-DavisNeural",
            "gender": "male",
            "accent": "US",
            "description": "Giọng nam trầm, chuyên nghiệp - Nội dung học thuật",
            "recommended": False
        },
        "us_female_child": {
            "id": "en-US-AnaNeural",
            "gender": "female",
            "accent": "US",
            "description": "Giọng em bé - Học viên nhỏ tuổi",
            "recommended": False
        },
        
        # Giọng Anh (British English)
        "gb_female": {
            "id": "en-GB-SoniaNeural",
            "gender": "female",
            "accent": "GB",
            "description": "Chuẩn BBC, sang trọng",
            "recommended": True
        },
        "gb_male": {
            "id": "en-GB-RyanNeural",
            "gender": "male",
            "accent": "GB",
            "description": "Lịch lãm, chuyên nghiệp",
            "recommended": True
        },
        "gb_female_modern": {
            "id": "en-GB-LibbyNeural",
            "gender": "female",
            "accent": "GB",
            "description": "Trẻ trung, hiện đại",
            "recommended": False
        },
        
        # Giọng Úc (Australian)
        "au_female": {
            "id": "en-AU-NatashaNeural",
            "gender": "female",
            "accent": "AU",
            "description": "Giọng nữ Úc",
            "recommended": False
        },
        "au_male": {
            "id": "en-AU-WilliamNeural",
            "gender": "male",
            "accent": "AU",
            "description": "Giọng nam Úc",
            "recommended": False
        },
        
        # Giọng Canada
        "ca_female": {
            "id": "en-CA-ClaraNeural",
            "gender": "female",
            "accent": "CA",
            "description": "Giọng nữ Canada",
            "recommended": False
        },
        "ca_male": {
            "id": "en-CA-LiamNeural",
            "gender": "male",
            "accent": "CA",
            "description": "Giọng nam Canada",
            "recommended": False
        },
        
        # Giọng Ấn Độ (Indian English)
        "in_female": {
            "id": "en-IN-NeerjaNeural",
            "gender": "female",
            "accent": "IN",
            "description": "Giọng nữ Ấn Độ",
            "recommended": False
        },
        "in_male": {
            "id": "en-IN-PrabhatNeural",
            "gender": "male",
            "accent": "IN",
            "description": "Giọng nam Ấn Độ",
            "recommended": False
        },
    }
    
    # Cấu hình tốc độ theo trình độ học viên
    SPEED_LEVELS = {
        "beginner": -25,        # Người mới: chậm 25%
        "elementary": -15,      # Sơ cấp: chậm 15%
        "intermediate": 0,      # Trung cấp: bình thường
        "upper_intermediate": +5,  # Trung cấp cao: nhanh 5%
        "advanced": +10,        # Nâng cao: nhanh 10%
        "native": +15,          # Tốc độ người bản ngữ
    }
    
    # Cache settings
    CACHE_TTL_AUDIO = 3600 * 24 * 7  # 7 days for audio files
    CACHE_PREFIX = "edge_tts_audio"
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize Edge TTS Service.
        
        Args:
            output_dir: Directory to store audio files (default: MEDIA_ROOT/tts_audio)
        """
        if output_dir is None:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'tts_audio')
        
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.default_voice = getattr(settings, 'TTS_DEFAULT_VOICE_KEY', 'us_female_clear')
        self.default_speed_level = getattr(settings, 'TTS_DEFAULT_SPEED_LEVEL', 'intermediate')
        
        logger.info(f"EnglishTTSService initialized: output_dir={self.output_dir}")
    
    # =========================================================================
    # CORE TTS GENERATION
    # =========================================================================
    
    async def generate_speech(
        self,
        text: str,
        voice_key: str = None,
        speed_level: str = None,
        pitch: int = 0,
        filename: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """
        Generate speech audio from text.
        
        Args:
            text: Text to convert to speech
            voice_key: Voice key from VOICES dict (default: us_female_clear)
            speed_level: Student level (beginner/intermediate/advanced)
            pitch: Pitch adjustment (-20 to +20 Hz, 0 = default)
            filename: Custom filename (without extension)
            use_cache: Check cache before generating
        
        Returns:
            Path to generated audio file
        
        Raises:
            ValueError: If text is empty or voice_key invalid
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Use defaults if not specified
        voice_key = voice_key or self.default_voice
        speed_level = speed_level or self.default_speed_level
        
        # Validate voice
        if voice_key not in self.VOICES:
            logger.warning(f"Invalid voice_key '{voice_key}', using default")
            voice_key = self.default_voice
        
        # Get voice ID
        voice_id = self.VOICES[voice_key]["id"]
        
        # Get speed rate
        rate = self.SPEED_LEVELS.get(speed_level, 0)
        rate_str = f"{rate:+d}%"
        pitch_str = f"{pitch:+d}Hz"
        
        # Generate filename
        if filename is None:
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            filename = f"{voice_key}_{speed_level}_{text_hash}"
        
        output_path = os.path.join(self.output_dir, f"{filename}.mp3")
        
        # Check cache
        if use_cache and os.path.exists(output_path):
            logger.info(f"✅ Using cached audio: {filename}.mp3")
            return output_path
        
        # Mock mode for offline development
        if get_mock_tts_mode():
            return await self._generate_mock_audio(text, voice_id, output_path)
        
        # Generate with Edge TTS
        try:
            logger.info(f"🔊 Generating audio: '{text[:50]}...' with {voice_key} ({speed_level})")
            
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_id,
                rate=rate_str,
                pitch=pitch_str
            )
            
            await communicate.save(output_path)
            
            # Validate file
            if not os.path.exists(output_path):
                raise Exception(f"Audio file not created: {output_path}")
            
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Audio generated: {filename}.mp3 ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {e}")
            # Clean up failed file
            if os.path.exists(output_path):
                os.remove(output_path)
            raise Exception(f"TTS generation failed: {e}")
    
    async def _generate_mock_audio(self, text: str, voice_id: str, output_path: str) -> str:
        """Generate mock audio for offline testing."""
        logger.info(f"[MOCK] Generating audio: text='{text[:50]}...', voice={voice_id}")
        
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
            
            # Create 2-second sine wave tone (440 Hz = A note)
            duration_ms = 2000
            frequency = 440
            
            sine_tone = Sine(frequency, sample_rate=44100).to_audio_segment(duration=duration_ms)
            sine_tone.export(output_path, format="mp3", bitrate="192k")
            
            logger.info(f"[MOCK] Audio created: {output_path}")
            
        except ImportError:
            # Fallback: create empty MP3
            logger.warning("[MOCK] pydub not available, creating empty file")
            with open(output_path, 'wb') as f:
                f.write(b'')  # Empty file for testing
        
        return output_path
    
    # =========================================================================
    # SPECIALIZED GENERATION METHODS
    # =========================================================================
    
    async def generate_word_pronunciation(
        self,
        word: str,
        accent: str = "us",
        repeat: int = 1,
        speed_level: str = "beginner"
    ) -> str:
        """
        Generate audio for word pronunciation.
        
        Args:
            word: Word to pronounce
            accent: "us" or "gb"
            repeat: Number of times to repeat (default: 1)
            speed_level: Speed level (default: beginner for clarity)
        
        Returns:
            Path to audio file
        """
        # Select voice
        voice_key = "us_female_clear" if accent == "us" else "gb_female"
        
        # Create repeated text
        text = " ... ".join([word] * repeat)
        
        # Sanitize filename - remove invalid characters for Windows
        import re
        safe_word = re.sub(r'[<>:"/\\|?*]', '_', word.lower())
        safe_word = safe_word.replace(' ', '_')
        
        filename = f"word_{safe_word}_{accent}_{repeat}x"
        
        return await self.generate_speech(
            text=text,
            voice_key=voice_key,
            speed_level=speed_level,
            filename=filename
        )
    
    async def generate_sentence_audio(
        self,
        sentence: str,
        student_level: str = "intermediate",
        voice_type: str = "female",
        accent: str = "us"
    ) -> str:
        """
        Generate audio for a sentence.
        
        Args:
            sentence: Sentence to read
            student_level: Student proficiency level
            voice_type: "female" or "male"
            accent: "us" or "gb"
        
        Returns:
            Path to audio file
        """
        # Select voice
        if accent == "us":
            voice_key = "us_female_clear" if voice_type == "female" else "us_male_standard"
        else:
            voice_key = "gb_female" if voice_type == "female" else "gb_male"
        
        return await self.generate_speech(
            text=sentence,
            voice_key=voice_key,
            speed_level=student_level
        )
    
    async def generate_conversation(
        self,
        dialogues: List[Dict[str, str]],
        student_level: str = "intermediate"
    ) -> List[str]:
        """
        Generate audio for conversation (multiple speakers).
        
        Args:
            dialogues: List of {"speaker": "A/B", "text": "..."}
            student_level: Student level
        
        Returns:
            List of audio file paths
        
        Example:
            >>> dialogues = [
            ...     {"speaker": "A", "text": "Hello, how are you?"},
            ...     {"speaker": "B", "text": "I'm fine, thank you!"}
            ... ]
            >>> audio_files = await tts.generate_conversation(dialogues)
        """
        audio_files = []
        
        for i, dialogue in enumerate(dialogues):
            speaker = dialogue["speaker"]
            text = dialogue["text"]
            
            # Alternate voices
            voice_key = "us_female_clear" if speaker == "A" else "us_male_standard"
            
            audio_path = await self.generate_speech(
                text=text,
                voice_key=voice_key,
                speed_level=student_level,
                filename=f"dialogue_{i}_{speaker}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
            )
            
            audio_files.append(audio_path)
        
        return audio_files
    
    async def generate_flashcard_audio(
        self,
        word: str,
        definition: str,
        example: str,
        accent: str = "us"
    ) -> Dict[str, str]:
        """
        Generate complete audio set for a flashcard.
        
        Args:
            word: The vocabulary word
            definition: Word definition
            example: Example sentence
            accent: "us" or "gb"
        
        Returns:
            Dict with keys: word, definition, example (audio paths)
        """
        voice_key = "us_female_clear" if accent == "us" else "gb_female"
        
        # Generate word pronunciation (repeat 2 times, slow)
        word_audio = await self.generate_word_pronunciation(
            word=word,
            accent=accent,
            repeat=2,
            speed_level="beginner"
        )
        
        # Generate definition (slow for comprehension)
        definition_audio = await self.generate_speech(
            text=definition,
            voice_key=voice_key,
            speed_level="beginner",
            filename=f"flashcard_def_{word.lower().replace(' ', '_')}"
        )
        
        # Generate example (normal speed)
        example_audio = await self.generate_speech(
            text=example,
            voice_key=voice_key,
            speed_level="intermediate",
            filename=f"flashcard_ex_{word.lower().replace(' ', '_')}"
        )
        
        return {
            "word": word_audio,
            "definition": definition_audio,
            "example": example_audio
        }
    
    async def generate_reading_passage(
        self,
        passage: str,
        student_level: str = "advanced",
        voice_key: str = "us_male_professional"
    ) -> str:
        """
        Generate audio for reading comprehension passage.
        
        Args:
            passage: Text passage to read
            student_level: Student level
            voice_key: Specific voice to use
        
        Returns:
            Path to audio file
        """
        return await self.generate_speech(
            text=passage.strip(),
            voice_key=voice_key,
            speed_level=student_level
        )
    
    # =========================================================================
    # SYNCHRONOUS WRAPPERS
    # =========================================================================
    
    def generate_speech_sync(self, *args, **kwargs) -> str:
        """Synchronous wrapper for generate_speech."""
        return asyncio.run(self.generate_speech(*args, **kwargs))
    
    def generate_word_pronunciation_sync(self, *args, **kwargs) -> str:
        """Synchronous wrapper for generate_word_pronunciation."""
        return asyncio.run(self.generate_word_pronunciation(*args, **kwargs))
    
    def generate_sentence_audio_sync(self, *args, **kwargs) -> str:
        """Synchronous wrapper for generate_sentence_audio."""
        return asyncio.run(self.generate_sentence_audio(*args, **kwargs))
    
    def generate_conversation_sync(self, *args, **kwargs) -> List[str]:
        """Synchronous wrapper for generate_conversation."""
        return asyncio.run(self.generate_conversation(*args, **kwargs))
    
    def generate_flashcard_audio_sync(self, *args, **kwargs) -> Dict[str, str]:
        """Synchronous wrapper for generate_flashcard_audio."""
        return asyncio.run(self.generate_flashcard_audio(*args, **kwargs))
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    @staticmethod
    async def list_all_english_voices() -> List[Dict]:
        """
        Get all available English voices from Edge TTS.
        
        Returns:
            List of voice information dicts
        """
        logger.info("📋 Fetching all English voices from Edge TTS...")
        
        try:
            voices = await edge_tts.list_voices()
            
            english_voices = [
                {
                    "name": v["ShortName"],
                    "locale": v["Locale"],
                    "gender": v["Gender"],
                    "display": f"{v['ShortName']} - {v['Locale']} ({v['Gender']})"
                }
                for v in voices
                if v["Locale"].startswith("en-")
            ]
            
            logger.info(f"✅ Found {len(english_voices)} English voices")
            return english_voices
            
        except Exception as e:
            logger.error(f"Failed to fetch voices: {e}")
            return []
    
    @classmethod
    def get_voice_info(cls, voice_key: str) -> Optional[Dict]:
        """Get information about a specific voice."""
        return cls.VOICES.get(voice_key)
    
    @classmethod
    def get_recommended_voices(cls) -> List[Tuple[str, Dict]]:
        """Get list of recommended voices."""
        return [(k, v) for k, v in cls.VOICES.items() if v.get("recommended")]
    
    @classmethod
    def select_voice_by_criteria(
        cls,
        gender: Optional[str] = None,
        accent: Optional[str] = None,
        recommended_only: bool = True
    ) -> str:
        """
        Select voice by criteria.
        
        Args:
            gender: "male" or "female"
            accent: "US", "GB", "AU", "CA", "IN"
            recommended_only: Only select from recommended voices
        
        Returns:
            Voice key
        """
        candidates = []
        
        for voice_key, voice_info in cls.VOICES.items():
            # Skip non-recommended if requested
            if recommended_only and not voice_info.get("recommended"):
                continue
            
            # Check gender match
            if gender and voice_info.get("gender") != gender.lower():
                continue
            
            # Check accent match
            if accent and voice_info.get("accent") != accent.upper():
                continue
            
            candidates.append(voice_key)
        
        # Return first match or default
        return candidates[0] if candidates else "us_female_clear"
    
    def get_audio_url(self, audio_path: str) -> str:
        """
        Convert local audio path to URL.
        
        Args:
            audio_path: Local file path
        
        Returns:
            URL to access the audio
        """
        # Convert absolute path to relative from MEDIA_ROOT
        relative_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
        # Build URL
        return os.path.join(settings.MEDIA_URL, relative_path).replace('\\', '/')
    
    def cleanup_old_files(self, days: int = 7):
        """
        Remove audio files older than specified days.
        
        Args:
            days: Keep files newer than this many days
        """
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        removed_count = 0
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            # Check file age
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_time < cutoff_time:
                try:
                    os.remove(filepath)
                    removed_count += 1
                    logger.info(f"Removed old audio: {filename}")
                except Exception as e:
                    logger.error(f"Failed to remove {filename}: {e}")
        
        logger.info(f"Cleanup complete: {removed_count} files removed")


# =========================================================================
# SINGLETON INSTANCE
# =========================================================================

# Global instance for easy access
_tts_service_instance = None


def get_tts_service() -> EnglishTTSService:
    """
    Get singleton TTS service instance.
    
    Usage:
        >>> from apps.curriculum.services.edge_tts_service import get_tts_service
        >>> tts = get_tts_service()
        >>> audio = await tts.generate_word_pronunciation("hello")
    """
    global _tts_service_instance
    
    if _tts_service_instance is None:
        _tts_service_instance = EnglishTTSService()
    
    return _tts_service_instance
