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
        
        try:
            # Generate audio file
            temp_audio_path = tts_service.generate_audio_sync(
                text=text_to_speak,
                voice=voice_id
            )
        except Exception as audio_error:
            logger.error(f"TTS generation error for phoneme {phoneme_id}: {audio_error}")
            # Retry with exponential backoff for transient errors
            raise self.retry(exc=audio_error, countdown=60)
        
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
            # Use phoneme ID instead of IPA symbol to avoid special character issues
            file_name = f"phoneme_{phoneme.id}_{voice_id.replace('-', '_')}.mp3"
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
