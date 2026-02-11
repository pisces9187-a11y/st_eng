"""
Celery Tasks for Flashcard Audio Generation

Background tasks for TTS audio generation:
- Async audio generation for individual words
- Batch audio generation for decks
- Cache cleanup
- Audio regeneration

Usage:
    from apps.vocabulary.tasks import generate_flashcard_audio_async
    
    # Queue audio generation
    generate_flashcard_audio_async.delay(
        word="hello",
        voice="us_male",
        speed="normal"
    )
"""

import logging
from celery import shared_task
from django.core.cache import cache
from services.tts_flashcard_service import get_tts_service

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_flashcard_audio_async(self, word: str, voice: str = 'us_male', speed: str = 'normal'):
    """
    Generate audio for a flashcard word asynchronously.
    
    Args:
        word: The word to generate audio for
        voice: Voice identifier (us_male, us_female, uk_male, uk_female)
        speed: Speed identifier (slow, normal, fast)
        
    Returns:
        Audio URL or None
    """
    try:
        logger.info(f"[Celery] Generating audio for '{word}' (voice={voice}, speed={speed})")
        
        tts_service = get_tts_service()
        audio_url = tts_service.generate_audio(word, voice, speed)
        
        if audio_url:
            logger.info(f"[Celery] Successfully generated audio: {audio_url}")
            return audio_url
        else:
            logger.error(f"[Celery] Failed to generate audio for '{word}'")
            return None
            
    except Exception as e:
        logger.error(f"[Celery] Error generating audio for '{word}': {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def generate_deck_audio_batch(deck_id: int, voice: str = 'us_male', speed: str = 'normal'):
    """
    Generate audio for all flashcards in a deck.
    
    Args:
        deck_id: FlashcardDeck ID
        voice: Voice identifier
        speed: Speed identifier
        
    Returns:
        Dictionary with generation statistics
    """
    from apps.vocabulary.models import FlashcardDeck, Flashcard
    
    try:
        deck = FlashcardDeck.objects.get(id=deck_id)
        flashcards = Flashcard.objects.filter(deck=deck).select_related('word')
        
        logger.info(f"[Celery] Starting batch audio generation for deck '{deck.name}' ({flashcards.count()} cards)")
        
        tts_service = get_tts_service()
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for flashcard in flashcards:
            word = flashcard.word.text
            
            # Check if audio already exists
            existing_url = tts_service.get_audio_url(word, voice, speed)
            if existing_url:
                skipped_count += 1
                continue
            
            # Generate audio
            audio_url = tts_service.generate_audio(word, voice, speed)
            
            if audio_url:
                success_count += 1
            else:
                failed_count += 1
        
        result = {
            'deck_id': deck_id,
            'deck_name': deck.name,
            'total_cards': flashcards.count(),
            'success': success_count,
            'failed': failed_count,
            'skipped': skipped_count,
        }
        
        logger.info(f"[Celery] Batch generation complete: {result}")
        return result
        
    except FlashcardDeck.DoesNotExist:
        logger.error(f"[Celery] Deck {deck_id} not found")
        return {'error': 'Deck not found'}
    except Exception as e:
        logger.error(f"[Celery] Error in batch generation: {e}")
        return {'error': str(e)}


@shared_task
def clean_expired_flashcard_audio():
    """
    Clean up audio files that haven't been accessed in 30+ days.
    
    This task runs daily via Celery Beat to manage storage space.
    
    Returns:
        Dictionary with cleanup statistics
    """
    from datetime import datetime, timedelta
    from pathlib import Path
    from django.conf import settings
    
    try:
        audio_dir = Path(settings.MEDIA_ROOT) / 'flashcard_audio'
        
        if not audio_dir.exists():
            logger.info("[Celery] Audio directory doesn't exist, nothing to clean")
            return {'deleted': 0, 'kept': 0}
        
        cutoff_date = datetime.now() - timedelta(days=30)
        deleted_count = 0
        kept_count = 0
        
        for audio_file in audio_dir.glob('*.mp3'):
            # Check last access time
            last_access = datetime.fromtimestamp(audio_file.stat().st_atime)
            
            if last_access < cutoff_date:
                # Delete old file
                audio_file.unlink()
                deleted_count += 1
                logger.debug(f"[Celery] Deleted old audio: {audio_file.name}")
            else:
                kept_count += 1
        
        result = {
            'deleted': deleted_count,
            'kept': kept_count,
            'cutoff_date': cutoff_date.isoformat(),
        }
        
        logger.info(f"[Celery] Audio cleanup complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"[Celery] Error in audio cleanup: {e}")
        return {'error': str(e)}


@shared_task
def regenerate_flashcard_audio(word: str, voice: str = 'us_male', speed: str = 'normal'):
    """
    Force regeneration of audio for a word (replaces existing).
    
    Args:
        word: The word to regenerate
        voice: Voice identifier
        speed: Speed identifier
        
    Returns:
        New audio URL or None
    """
    try:
        logger.info(f"[Celery] Regenerating audio for '{word}'")
        
        tts_service = get_tts_service()
        audio_url = tts_service.generate_audio(word, voice, speed, force_regenerate=True)
        
        if audio_url:
            logger.info(f"[Celery] Successfully regenerated audio: {audio_url}")
            return audio_url
        else:
            logger.error(f"[Celery] Failed to regenerate audio for '{word}'")
            return None
            
    except Exception as e:
        logger.error(f"[Celery] Error regenerating audio: {e}")
        return None
