"""
TTS Service using Microsoft Edge TTS API.

This service handles:
- Text-to-speech generation
- Voice selection
- Audio file creation
- Quality validation

Mock mode available for offline development (no internet required)
"""

import asyncio
import tempfile
import os
import logging
from pathlib import Path
from datetime import timedelta

import edge_tts
from django.conf import settings
from django.core.files import File
from django.utils import timezone

logger = logging.getLogger(__name__)

# Mock mode setting - check dynamically (don't cache at module load)
# This allows environment changes without reload
def get_mock_tts_mode():
    """Check if mock TTS mode is enabled."""
    # Check environment variable first, then settings
    env_mock = os.environ.get('MOCK_TTS', '').lower()
    if env_mock in ('true', 'false'):
        return env_mock == 'true'
    return getattr(settings, 'MOCK_TTS_MODE', False)


class TTSService:
    """
    Service for generating TTS audio using Edge-TTS.
    
    Usage:
        service = TTSService()
        audio_path = await service.generate_audio(
            text="Hello",
            voice="en-US-AriaNeural",
            rate="-30%"
        )
    """
    
    def __init__(self):
        self.default_voice = settings.TTS_DEFAULT_VOICE
        self.rate = settings.TTS_RATE
        self.volume = settings.TTS_VOLUME
    
    async def generate_audio(
        self,
        text: str,
        voice: str = None,
        rate: str = None,
        output_path: str = None
    ) -> str:
        """
        Generate TTS audio asynchronously.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (default: settings.TTS_DEFAULT_VOICE)
            rate: Speech rate (default: settings.TTS_RATE)
            output_path: Where to save audio (default: temp file)
        
        Returns:
            Path to generated audio file
        
        Raises:
            Exception: If TTS generation fails
        """
        voice = voice or self.default_voice
        rate = rate or self.rate
        
        # Create temporary file if no output path specified
        if not output_path:
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.mp3',
                prefix='tts_'
            )
            output_path = temp_file.name
            temp_file.close()
        
        try:
            # Mock mode for offline development
            if get_mock_tts_mode():
                logger.info(f"[MOCK] Generating TTS (mock mode): text='{text}', voice={voice}")
                # Create audible test audio (sine wave tone) using pydub
                try:
                    from pydub import AudioSegment
                    from pydub.generators import Sine
                    import io
                    
                    # Create audible sine wave tone (440 Hz = A note)
                    duration_ms = 2000  # 2 seconds
                    frequency = 440  # Hz (audible frequency)
                    
                    # Generate sine wave tone
                    sine_tone = Sine(frequency, sample_rate=44100).to_audio_segment(duration=duration_ms)
                    
                    # Export to MP3
                    mp3_buffer = io.BytesIO()
                    sine_tone.export(mp3_buffer, format="mp3", bitrate="192k")
                    mp3_data = mp3_buffer.getvalue()
                    
                    with open(output_path, 'wb') as f:
                        f.write(mp3_data)
                    
                    logger.info(f"[MOCK] Audible tone created: {output_path} ({len(mp3_data)} bytes, 440Hz)")
                    
                except Exception as e:
                    # Fallback: create using wave module (WAV format with sine wave)
                    logger.warning(f"[MOCK] pydub tone export failed: {e}, using WAV fallback")
                    import wave
                    import math
                    import struct
                    
                    # Create WAV with audible sine wave
                    duration = 2  # seconds
                    sample_rate = 44100
                    frequency = 440  # Hz (A note)
                    num_samples = duration * sample_rate
                    
                    # Convert output_path from .mp3 to .wav
                    wav_path = output_path.replace('.mp3', '.wav')
                    
                    # Generate sine wave samples and write directly
                    amplitude = 30000  # reduced amplitude for 16-bit
                    
                    # Write WAV file
                    with wave.open(wav_path, 'w') as wav_file:
                        wav_file.setnchannels(1)  # mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(sample_rate)
                        
                        # Generate and write samples in chunks
                        for i in range(num_samples):
                            value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                            # Clamp to 16-bit signed range
                            value = max(-32768, min(32767, value))
                            # Write as 16-bit signed little-endian
                            wav_file.writeframes(struct.pack('<h', value))
                    
                    # Rename WAV to MP3 (not ideal but works for testing)
                    import shutil
                    shutil.move(wav_path, output_path)
                    logger.info(f"[MOCK] WAV tone created (440Hz): {output_path}")
                
                return output_path
            
            # Real Edge-TTS API
            try:
                # Create TTS communicate object
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice,
                    rate=rate,
                    volume=self.volume
                )
                
                # Generate audio
                logger.info(f"Generating TTS: text='{text}', voice={voice}, rate={rate}")
                await communicate.save(output_path)
                
                # Validate file was created
                if not os.path.exists(output_path):
                    raise Exception(f"TTS file not created: {output_path}")
                
                file_size = os.path.getsize(output_path)
                logger.info(f"TTS generated successfully: {output_path} ({file_size} bytes)")
                
                return output_path
                
            except Exception as e:
                # Fallback to pyttsx3 (offline TTS)
                logger.warning(f"Edge TTS failed ({e}), falling back to pyttsx3...")
                try:
                    import pyttsx3
                    
                    engine = pyttsx3.init()
                    # Set properties for better audio
                    engine.setProperty('rate', 150)  # Speed
                    engine.setProperty('volume', 0.9)  # Volume
                    
                    # Save to MP3
                    engine.save_to_file(text, output_path)
                    engine.runAndWait()
                    engine.stop()
                    
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        logger.info(f"[OFFLINE] TTS generated via pyttsx3: {output_path} ({file_size} bytes)")
                        return output_path
                    else:
                        raise Exception(f"pyttsx3 failed to create file")
                        
                except Exception as fallback_error:
                    logger.error(f"pyttsx3 fallback also failed: {fallback_error}")
                    raise Exception(f"Both Edge TTS and pyttsx3 failed: {e} -> {fallback_error}")
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            # Clean up failed file
            if os.path.exists(output_path):
                os.remove(output_path)
            raise
    
    def generate_audio_sync(self, text: str, voice: str = None, rate: str = None) -> str:
        """
        Synchronous wrapper for generate_audio.
        
        Use this in Celery tasks or Django views.
        """
        return asyncio.run(self.generate_audio(text, voice, rate))
    
    @staticmethod
    def get_available_voices():
        """
        Get list of available voices from settings.
        
        Returns:
            dict: Voice ID -> metadata
        """
        return settings.TTS_VOICES
    
    @staticmethod
    def select_voice(gender: str = None, accent: str = None) -> str:
        """
        Select appropriate voice based on criteria.
        
        Args:
            gender: 'male' or 'female'
            accent: 'US', 'UK', 'AU'
        
        Returns:
            Voice ID
        """
        voices = settings.TTS_VOICES
        
        # Filter by criteria
        candidates = []
        for voice_id, metadata in voices.items():
            match = True
            if gender and metadata.get('gender') != gender:
                match = False
            if accent and metadata.get('accent') != accent:
                match = False
            
            if match:
                candidates.append(voice_id)
        
        # Return first match or default
        return candidates[0] if candidates else settings.TTS_DEFAULT_VOICE
