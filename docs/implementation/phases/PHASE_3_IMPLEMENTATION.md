# 🔊 PHASE 3 IMPLEMENTATION - TTS GENERATION & AUDIO PIPELINE

**Duration:** Week 5-6 (10 working days)  
**Focus:** Automated TTS Generation with Celery  
**Status:** READY TO PLAN

---

## 📋 MỤC TIÊU PHASE 3

### Xây Dựng Hệ Thống TTS Tự Động
1. **Async TTS Generation** - Generate audio trong background với Celery
2. **Batch Processing** - Xử lý hàng loạt phonemes chưa có audio
3. **Voice Management** - Quản lý nhiều giọng nói (male/female, accents)
4. **Audio Optimization** - Nén và tối ưu file size
5. **Admin Interface** - Giao diện quản lý TTS từ Django Admin

### Tech Stack
- **Celery:** Async task queue
- **Redis:** Message broker + result backend
- **Edge-TTS:** Microsoft Edge TTS API
- **Pydub:** Audio processing
- **Django Admin:** Extended admin interface

---

## 🗓️ TIMELINE CHI TIẾT

### **DAY 1-2: Setup Celery + Redis**
- Install & configure Celery
- Setup Redis as broker
- Test async tasks
- Create base task structure

### **DAY 3-4: TTS Generation Tasks**
- Implement generate_phoneme_audio task
- Add voice selection logic
- Error handling & retry mechanism
- Audio file storage

### **DAY 5-6: Batch Processing**
- Bulk generation admin action
- Progress tracking
- Notification system
- Queue management

### **DAY 7-8: Audio Optimization**
- File compression
- Format conversion (MP3 optimization)
- Duration calculation
- Quality validation

### **DAY 9-10: Admin Interface & Testing**
- Django Admin extensions
- Task monitoring dashboard
- Error logs
- Performance testing

---

## 📁 FILE STRUCTURE

```
backend/
├── apps/curriculum/
│   ├── tasks.py                    # NEW: Celery tasks
│   ├── admin.py                    # MODIFY: Add TTS actions
│   └── services/
│       ├── audio_service.py        # EXISTING: Integrate with tasks
│       └── tts_service.py          # NEW: TTS generation logic
│
├── config/
│   ├── settings.py                 # MODIFY: Add Celery config
│   ├── celery.py                   # NEW: Celery app config
│   └── __init__.py                 # MODIFY: Import celery app
│
├── requirements/
│   └── base.txt                    # ADD: celery, redis, edge-tts, pydub
│
└── utils/
    └── audio_utils.py              # NEW: Audio processing utilities
```

---

## 🔧 DAY 1-2: SETUP CELERY + REDIS

### Objectives
- Install Celery + Redis
- Configure Celery with Django
- Test basic async tasks
- Setup monitoring

### Step 1: Install Dependencies

**File:** `backend/requirements/base.txt` (ADD)

```txt
# Async Task Queue
celery==5.3.4
redis==5.0.1

# TTS Engine
edge-tts==6.1.9

# Audio Processing
pydub==0.25.1
mutagen==1.47.0  # Audio metadata
```

### Step 2: Install Requirements

```bash
cd backend
pip install -r requirements/base.txt
```

### Step 3: Create Celery Configuration

**File:** `backend/config/celery.py` (NEW)

```python
"""
Celery Configuration for English Study Platform

This module configures Celery for async task processing:
- TTS audio generation
- Batch processing
- Periodic tasks (cache cleanup)

Setup:
    1. Start Redis: redis-server
    2. Start Celery Worker: celery -A config worker -l info
    3. Start Celery Beat: celery -A config beat -l info
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('english_study')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule (Periodic Tasks)
app.conf.beat_schedule = {
    # Clean expired TTS cache daily at 2 AM
    'clean-expired-audio-cache': {
        'task': 'apps.curriculum.tasks.clean_expired_audio_cache',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Generate missing audio for new phonemes daily at 3 AM
    'generate-missing-audio': {
        'task': 'apps.curriculum.tasks.generate_missing_audio_batch',
        'schedule': crontab(hour=3, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')
```

### Step 4: Update Django Settings

**File:** `backend/config/settings.py` (ADD)

```python
# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

# Celery Broker (Redis)
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Celery Result Backend
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Celery Task Settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Task result expiration (7 days)
CELERY_RESULT_EXPIRES = 60 * 60 * 24 * 7

# Task time limits
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit

# Task retry settings
CELERY_TASK_AUTORETRY_FOR = (Exception,)
CELERY_TASK_RETRY_KWARGS = {'max_retries': 3}
CELERY_TASK_RETRY_BACKOFF = True  # Exponential backoff

# Task routing (optional - for multiple queues)
CELERY_TASK_ROUTES = {
    'apps.curriculum.tasks.generate_phoneme_audio': {'queue': 'tts'},
    'apps.curriculum.tasks.generate_audio_batch': {'queue': 'tts'},
    'apps.curriculum.tasks.clean_expired_audio_cache': {'queue': 'maintenance'},
}

# Worker settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100  # Restart worker after 100 tasks

# ============================================================================
# TTS CONFIGURATION
# ============================================================================

# Edge-TTS Voice Settings
TTS_DEFAULT_VOICE = 'en-US-AriaNeural'  # Female, American
TTS_VOICES = {
    'en-US-AriaNeural': {'gender': 'female', 'accent': 'US'},
    'en-US-GuyNeural': {'gender': 'male', 'accent': 'US'},
    'en-GB-SoniaNeural': {'gender': 'female', 'accent': 'UK'},
    'en-GB-RyanNeural': {'gender': 'male', 'accent': 'UK'},
    'en-AU-NatashaNeural': {'gender': 'female', 'accent': 'AU'},
    'en-AU-WilliamNeural': {'gender': 'male', 'accent': 'AU'},
}

# TTS Generation Settings
TTS_RATE = '-30%'  # Slower for clarity
TTS_VOLUME = '+0%'  # Normal volume
TTS_CACHE_DAYS = 30  # Cache TTS audio for 30 days

# Audio Processing Settings
AUDIO_FORMAT = 'mp3'
AUDIO_BITRATE = '128k'  # Good quality, reasonable file size
AUDIO_SAMPLE_RATE = 44100  # CD quality
```

### Step 5: Initialize Celery App

**File:** `backend/config/__init__.py` (MODIFY)

```python
"""
Django configuration initialization.
Import Celery app to ensure it's loaded when Django starts.
"""

# Import celery app
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Step 6: Test Celery Setup

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
cd backend
celery -A config worker -l info

# Terminal 3: Start Celery Beat (for periodic tasks)
celery -A config beat -l info

# Terminal 4: Test task
python manage.py shell
>>> from config.celery import debug_task
>>> result = debug_task.delay()
>>> result.get()
```

---

## 🎤 DAY 3-4: TTS GENERATION TASKS

### Objectives
- Create TTS generation Celery tasks
- Implement voice selection logic
- Handle errors and retries
- Store audio files properly

### Step 1: Create TTS Service

**File:** `backend/apps/curriculum/services/tts_service.py` (NEW)

```python
"""
TTS Service using Microsoft Edge TTS API.

This service handles:
- Text-to-speech generation
- Voice selection
- Audio file creation
- Quality validation
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
```

### Step 2: Create Audio Utilities

**File:** `backend/utils/audio_utils.py` (NEW)

```python
"""
Audio processing utilities.

Functions:
- Calculate audio duration
- Compress audio files
- Convert audio formats
- Extract metadata
"""

import os
import logging
from pathlib import Path

from pydub import AudioSegment
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)


def get_audio_duration(file_path: str) -> float:
    """
    Get audio file duration in seconds.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Duration in seconds (float)
    """
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        logger.error(f"Failed to get duration for {file_path}: {e}")
        return 0.0


def optimize_audio(
    input_path: str,
    output_path: str = None,
    bitrate: str = '128k',
    sample_rate: int = 44100
) -> str:
    """
    Optimize audio file (compress, normalize).
    
    Args:
        input_path: Path to input audio
        output_path: Path to save optimized audio (default: overwrite)
        bitrate: Target bitrate (e.g., '128k', '192k')
        sample_rate: Target sample rate (e.g., 44100, 48000)
    
    Returns:
        Path to optimized audio file
    """
    if not output_path:
        output_path = input_path
    
    try:
        # Load audio
        audio = AudioSegment.from_file(input_path)
        
        # Normalize loudness
        audio = audio.normalize()
        
        # Export with optimization
        audio.export(
            output_path,
            format='mp3',
            bitrate=bitrate,
            parameters=[
                "-ar", str(sample_rate),  # Sample rate
                "-ac", "1",  # Mono (phonemes don't need stereo)
                "-q:a", "2"  # VBR quality (0=best, 9=worst)
            ]
        )
        
        # Log file size reduction
        original_size = os.path.getsize(input_path)
        optimized_size = os.path.getsize(output_path)
        reduction = ((original_size - optimized_size) / original_size) * 100
        
        logger.info(
            f"Audio optimized: {input_path} -> {output_path} "
            f"({original_size} -> {optimized_size} bytes, {reduction:.1f}% reduction)"
        )
        
        return output_path
        
    except Exception as e:
        logger.error(f"Audio optimization failed: {e}")
        return input_path  # Return original if optimization fails


def convert_audio_format(
    input_path: str,
    output_format: str = 'mp3',
    output_path: str = None
) -> str:
    """
    Convert audio to different format.
    
    Args:
        input_path: Path to input audio
        output_format: Target format ('mp3', 'wav', 'ogg')
        output_path: Path to save converted audio
    
    Returns:
        Path to converted audio
    """
    if not output_path:
        output_path = str(Path(input_path).with_suffix(f'.{output_format}'))
    
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=output_format)
        
        logger.info(f"Audio converted: {input_path} -> {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        raise
```

### Step 3: Create Celery Tasks

**File:** `backend/apps/curriculum/tasks.py` (NEW)

```python
"""
Celery tasks for English Study Platform.

Tasks:
- generate_phoneme_audio: Generate TTS audio for a single phoneme
- generate_audio_batch: Generate audio for multiple phonemes
- clean_expired_audio_cache: Remove expired TTS audio files
- optimize_audio_files: Compress and optimize audio files
"""

import os
import logging
from datetime import timedelta
from pathlib import Path

from celery import shared_task, group, chord
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from django.db import transaction

from apps.curriculum.models import Phoneme, AudioSource, AudioCache
from apps.curriculum.services.tts_service import TTSService
from utils.audio_utils import get_audio_duration, optimize_audio

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_phoneme_audio(
    self,
    phoneme_id: int,
    voice_id: str = None,
    force_regenerate: bool = False
):
    """
    Generate TTS audio for a single phoneme.
    
    Args:
        phoneme_id: ID of the phoneme
        voice_id: TTS voice to use (optional)
        force_regenerate: Regenerate even if audio exists
    
    Returns:
        dict: {
            'success': bool,
            'phoneme_id': int,
            'audio_source_id': int,
            'message': str
        }
    """
    try:
        # Get phoneme
        try:
            phoneme = Phoneme.objects.get(id=phoneme_id)
        except Phoneme.DoesNotExist:
            return {
                'success': False,
                'phoneme_id': phoneme_id,
                'message': 'Phoneme not found'
            }
        
        # Check if audio already exists
        if not force_regenerate:
            existing_tts = AudioSource.objects.filter(
                phoneme=phoneme,
                source_type='tts',
                cached_until__gt=timezone.now()
            ).first()
            
            if existing_tts:
                return {
                    'success': True,
                    'phoneme_id': phoneme_id,
                    'audio_source_id': existing_tts.id,
                    'message': 'Audio already exists (skipped)'
                }
        
        # Select voice
        if not voice_id:
            voice_id = settings.TTS_DEFAULT_VOICE
        
        # Generate TTS audio
        logger.info(f"Generating TTS for phoneme /{phoneme.ipa_symbol}/ (ID: {phoneme_id})")
        
        tts_service = TTSService()
        
        # Use IPA symbol as text for TTS (or example word)
        # For better pronunciation, use a full word containing the phoneme
        text_to_speak = phoneme.vietnamese_approx or phoneme.ipa_symbol
        
        # Generate audio file
        temp_audio_path = tts_service.generate_audio_sync(
            text=text_to_speak,
            voice=voice_id
        )
        
        # Optimize audio
        optimized_path = optimize_audio(
            temp_audio_path,
            bitrate=settings.AUDIO_BITRATE,
            sample_rate=settings.AUDIO_SAMPLE_RATE
        )
        
        # Get audio duration
        duration = get_audio_duration(optimized_path)
        
        # Save to database
        with transaction.atomic():
            # Create or update AudioSource
            audio_source, created = AudioSource.objects.update_or_create(
                phoneme=phoneme,
                source_type='tts',
                voice_id=voice_id,
                defaults={
                    'language': 'en-US',
                    'audio_duration': duration,
                    'cached_until': timezone.now() + timedelta(days=settings.TTS_CACHE_DAYS),
                    'metadata': {
                        'tts_rate': settings.TTS_RATE,
                        'tts_volume': settings.TTS_VOLUME,
                        'generated_by': 'celery_task',
                        'task_id': self.request.id
                    }
                }
            )
            
            # Save audio file
            file_name = f"{phoneme.ipa_symbol.replace('/', '')}_{voice_id}.mp3"
            with open(optimized_path, 'rb') as f:
                audio_source.audio_file.save(file_name, File(f), save=True)
            
            # Create cache record
            file_size = os.path.getsize(optimized_path)
            AudioCache.objects.update_or_create(
                audio_source=audio_source,
                defaults={
                    'file_size': file_size,
                    'usage_count': 0
                }
            )
        
        # Clean up temp files
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if optimized_path != temp_audio_path and os.path.exists(optimized_path):
            os.remove(optimized_path)
        
        logger.info(
            f"✅ TTS generated successfully for /{phoneme.ipa_symbol}/ "
            f"(AudioSource ID: {audio_source.id})"
        )
        
        return {
            'success': True,
            'phoneme_id': phoneme_id,
            'audio_source_id': audio_source.id,
            'message': 'Audio generated successfully'
        }
        
    except Exception as exc:
        logger.error(f"❌ TTS generation failed for phoneme {phoneme_id}: {exc}")
        
        # Retry with exponential backoff
        raise self.retry(exc=exc)


@shared_task
def generate_audio_batch(phoneme_ids: list, voice_id: str = None):
    """
    Generate TTS audio for multiple phonemes in parallel.
    
    Args:
        phoneme_ids: List of phoneme IDs
        voice_id: Voice to use for all phonemes
    
    Returns:
        dict: Summary of batch generation
    """
    logger.info(f"Starting batch TTS generation for {len(phoneme_ids)} phonemes")
    
    # Create task group for parallel execution
    job = group(
        generate_phoneme_audio.s(phoneme_id, voice_id)
        for phoneme_id in phoneme_ids
    )
    
    # Execute and wait for results
    result = job.apply_async()
    results = result.get()
    
    # Summarize results
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    summary = {
        'total': len(phoneme_ids),
        'successful': successful,
        'failed': failed,
        'voice_id': voice_id,
        'results': results
    }
    
    logger.info(
        f"Batch TTS generation completed: "
        f"{successful}/{len(phoneme_ids)} successful, {failed} failed"
    )
    
    return summary


@shared_task
def generate_missing_audio_batch():
    """
    Periodic task to generate TTS for phonemes without audio.
    
    Runs daily via Celery Beat.
    """
    # Get phonemes without audio
    phonemes_without_audio = Phoneme.objects.filter(
        audio_sources__isnull=True
    ).values_list('id', flat=True)
    
    count = len(phonemes_without_audio)
    
    if count == 0:
        logger.info("No phonemes missing audio")
        return {'generated': 0}
    
    logger.info(f"Found {count} phonemes without audio, generating TTS...")
    
    # Generate audio in batch
    result = generate_audio_batch(list(phonemes_without_audio))
    
    return result


@shared_task
def clean_expired_audio_cache():
    """
    Remove expired TTS audio files from storage.
    
    Runs daily via Celery Beat.
    """
    # Find expired TTS audio
    expired_audio = AudioSource.objects.filter(
        source_type='tts',
        cached_until__lt=timezone.now()
    )
    
    count = expired_audio.count()
    
    if count == 0:
        logger.info("No expired audio to clean")
        return {'cleaned': 0}
    
    logger.info(f"Cleaning {count} expired TTS audio files...")
    
    # Delete files and records
    for audio in expired_audio:
        # Delete physical file
        if audio.audio_file:
            audio.audio_file.delete(save=False)
        
        # Delete cache record
        try:
            audio.cache.delete()
        except AudioCache.DoesNotExist:
            pass
        
        # Delete audio source
        audio.delete()
    
    logger.info(f"✅ Cleaned {count} expired audio files")
    
    return {'cleaned': count}
```

---

## 📊 DAY 5-6: ADMIN INTERFACE FOR TTS

### Objectives
- Add bulk generation actions to Django Admin
- Progress monitoring
- Error handling UI
- Task status display

### Implementation

**File:** `backend/apps/curriculum/admin.py` (MODIFY AudioSourceAdmin)

```python
from django.contrib import admin, messages
from django.utils.html import format_html
from .models import AudioSource, AudioCache, Phoneme
from .tasks import generate_phoneme_audio, generate_audio_batch


@admin.register(AudioSource)
class AudioSourceAdmin(admin.ModelAdmin):
    # ... existing configuration ...
    
    actions = [
        'set_as_preferred',
        'clear_cache',
        'generate_tts_audio',  # NEW
        'regenerate_tts_audio',  # NEW
    ]
    
    def generate_tts_audio(self, request, queryset):
        """
        Generate TTS audio for selected phonemes (only if missing).
        """
        phoneme_ids = []
        
        for audio in queryset:
            phoneme = audio.phoneme
            
            # Check if TTS audio already exists
            has_tts = AudioSource.objects.filter(
                phoneme=phoneme,
                source_type='tts',
                cached_until__gt=timezone.now()
            ).exists()
            
            if not has_tts:
                phoneme_ids.append(phoneme.id)
        
        if not phoneme_ids:
            self.message_user(
                request,
                "All selected phonemes already have TTS audio",
                level=messages.INFO
            )
            return
        
        # Start batch generation task
        task = generate_audio_batch.delay(phoneme_ids)
        
        self.message_user(
            request,
            f"Started TTS generation for {len(phoneme_ids)} phonemes. "
            f"Task ID: {task.id}",
            level=messages.SUCCESS
        )
    
    generate_tts_audio.short_description = "Generate TTS audio (if missing)"
    
    def regenerate_tts_audio(self, request, queryset):
        """
        Regenerate TTS audio for selected phonemes (force overwrite).
        """
        phoneme_ids = [audio.phoneme.id for audio in queryset]
        
        # Start batch generation with force_regenerate=True
        task = group(
            generate_phoneme_audio.s(pid, force_regenerate=True)
            for pid in phoneme_ids
        ).apply_async()
        
        self.message_user(
            request,
            f"Started TTS regeneration for {len(phoneme_ids)} phonemes. "
            f"Check Celery logs for progress.",
            level=messages.SUCCESS
        )
    
    regenerate_tts_audio.short_description = "Regenerate TTS audio (force)"


# Add action to Phoneme admin as well
@admin.register(Phoneme)
class PhonemeAdmin(admin.ModelAdmin):
    # ... existing configuration ...
    
    actions = ['generate_missing_audio']
    
    def generate_missing_audio(self, request, queryset):
        """Generate TTS audio for phonemes without audio."""
        phoneme_ids = list(queryset.filter(
            audio_sources__isnull=True
        ).values_list('id', flat=True))
        
        if not phoneme_ids:
            self.message_user(
                request,
                "All selected phonemes already have audio",
                level=messages.INFO
            )
            return
        
        task = generate_audio_batch.delay(phoneme_ids)
        
        self.message_user(
            request,
            f"Started TTS generation for {len(phoneme_ids)} phonemes. "
            f"Task ID: {task.id}",
            level=messages.SUCCESS
        )
    
    generate_missing_audio.short_description = "Generate TTS for missing audio"
```

---

## ✅ PHASE 3 DELIVERABLES

### Backend Infrastructure
1. ✅ Celery + Redis setup
2. ✅ TTS Service with Edge-TTS
3. ✅ Async task queue
4. ✅ Batch processing
5. ✅ Audio optimization utilities

### Celery Tasks
1. ✅ `generate_phoneme_audio` - Single phoneme generation
2. ✅ `generate_audio_batch` - Bulk generation
3. ✅ `generate_missing_audio_batch` - Periodic task
4. ✅ `clean_expired_audio_cache` - Cleanup task

### Admin Features
1. ✅ Bulk TTS generation action
2. ✅ Force regeneration action
3. ✅ Task monitoring
4. ✅ Progress tracking

### Audio Quality
- ✅ MP3 optimization (128k bitrate)
- ✅ Mono audio (phonemes don't need stereo)
- ✅ Normalized loudness
- ✅ Duration calculation
- ✅ Metadata tracking

---

## 🚀 DEPLOYMENT CHECKLIST

```bash
# 1. Install Redis
sudo apt-get install redis-server
redis-server

# 2. Install Python dependencies
pip install -r requirements/base.txt

# 3. Run migrations
python manage.py migrate

# 4. Start Celery Worker
celery -A config worker -l info -Q tts,maintenance

# 5. Start Celery Beat (periodic tasks)
celery -A config beat -l info

# 6. Monitor with Flower (optional)
pip install flower
celery -A config flower
# Visit http://localhost:5555
```

---

## 📈 MONITORING & METRICS

### Key Metrics to Track
- TTS generation success rate
- Average generation time per phoneme
- Cache hit rate
- Storage usage
- Queue length
- Worker health

### Celery Monitoring Tools
1. **Flower:** Web-based monitoring UI
2. **Django Admin:** Custom task status page
3. **Logs:** CloudWatch/ELK Stack
4. **Alerts:** Email/Slack notifications on failures

---

## 🔒 SECURITY & RATE LIMITING

### Edge-TTS Rate Limits
- **Free tier:** No official limit, but be respectful
- **Recommendation:** Max 100 requests/minute
- **Implementation:** Celery task rate limit

```python
@shared_task(rate_limit='100/m')  # 100 per minute
def generate_phoneme_audio(...):
    ...
```

---

## 🎯 SUCCESS CRITERIA

Phase 3 is complete when:

- [ ] Celery + Redis running stable
- [ ] TTS generation works for all 44 phonemes
- [ ] Batch processing completes within 10 minutes
- [ ] Audio files optimized (< 50KB per phoneme)
- [ ] Admin actions work smoothly
- [ ] Periodic tasks run automatically
- [ ] Error handling covers edge cases
- [ ] Monitoring dashboard shows metrics
- [ ] Documentation updated

---

**Status:** READY FOR IMPLEMENTATION  
**Dependencies:** Phase 1 complete (AudioSource model exists)  
**Estimated Completion:** 10 working days  
**Next Phase:** Phase 4 - Testing & Optimization
