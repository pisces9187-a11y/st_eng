"""Services package for curriculum app.

This package contains business logic services that orchestrate
operations across multiple models and external APIs.

Modules:
- audio_service: PhonemeAudioService for audio management
- tts_service: TTS generation and caching (future)
- cache_service: Cache management utilities (future)
"""

from .audio_service import PhonemeAudioService

__all__ = [
    'PhonemeAudioService',
]
