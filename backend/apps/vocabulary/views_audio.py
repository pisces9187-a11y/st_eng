"""
Audio API Views for Flashcards

Provides endpoints for:
- Audio generation on-demand
- Audio streaming/download
- Voice configuration
- Batch audio generation
- Storage statistics

Authentication: JWT required for all endpoints
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.http import FileResponse, Http404
from django.core.cache import cache
from pathlib import Path

from services.tts_flashcard_service import get_tts_service
from apps.vocabulary.models import Flashcard, FlashcardDeck
from apps.vocabulary.tasks import generate_flashcard_audio_async, generate_deck_audio_batch

logger = logging.getLogger(__name__)


class FlashcardAudioViewSet(ViewSet):
    """
    ViewSet for flashcard audio operations.
    
    Endpoints:
        GET /audio/voices/ - List available voices
        POST /audio/generate/ - Generate audio for a word
        POST /audio/generate_batch/ - Generate audio for a deck
        GET /audio/stats/ - Get storage statistics
        GET /audio/stream/{word}/ - Stream audio file
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def voices(self, request):
        """
        Get list of available voices and speeds.
        
        Response:
            {
                "voices": [
                    {"id": "us_male", "name": "US Male", "code": "en-US-GuyNeural"},
                    ...
                ],
                "speeds": [
                    {"id": "slow", "name": "Slow (70%)", "rate": "-30%"},
                    ...
                ]
            }
        """
        tts_service = get_tts_service()
        voices_config = tts_service.get_available_voices()
        
        return Response(voices_config, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate audio for a word.
        
        Request Body:
            {
                "word": "hello",
                "voice": "us_male",  # Optional, default: us_male
                "speed": "normal",   # Optional, default: normal
                "async": true        # Optional, use Celery task
            }
        
        Response:
            {
                "word": "hello",
                "audio_url": "/media/flashcard_audio/hello_us_male_normal.mp3",
                "voice": "us_male",
                "speed": "normal",
                "cached": false,
                "task_id": "abc123"  # Only if async=true
            }
        """
        word = request.data.get('word')
        if not word:
            return Response(
                {'error': 'Word parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        voice = request.data.get('voice', 'us_male')
        speed = request.data.get('speed', 'normal')
        use_async = request.data.get('async', False)
        
        tts_service = get_tts_service()
        
        # Check cache first
        cache_key = tts_service.get_cache_key(word, voice, speed)
        cached_url = cache.get(cache_key)
        
        if cached_url:
            return Response({
                'word': word,
                'audio_url': cached_url,
                'voice': voice,
                'speed': speed,
                'cached': True,
            }, status=status.HTTP_200_OK)
        
        # Generate audio
        if use_async:
            # Queue Celery task
            task = generate_flashcard_audio_async.delay(word, voice, speed)
            
            return Response({
                'word': word,
                'voice': voice,
                'speed': speed,
                'cached': False,
                'async': True,
                'task_id': task.id,
                'message': 'Audio generation queued',
            }, status=status.HTTP_202_ACCEPTED)
        else:
            # Generate synchronously
            audio_url = tts_service.generate_audio(word, voice, speed)
            
            if audio_url:
                return Response({
                    'word': word,
                    'audio_url': audio_url,
                    'voice': voice,
                    'speed': speed,
                    'cached': False,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Failed to generate audio'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=False, methods=['post'])
    def generate_batch(self, request):
        """
        Generate audio for all flashcards in a deck.
        
        Request Body:
            {
                "deck_id": 1,
                "voice": "us_male",  # Optional
                "speed": "normal"    # Optional
            }
        
        Response:
            {
                "deck_id": 1,
                "deck_name": "Oxford A1",
                "task_id": "xyz789",
                "message": "Batch generation queued"
            }
        """
        deck_id = request.data.get('deck_id')
        if not deck_id:
            return Response(
                {'error': 'deck_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify deck exists
        try:
            deck = FlashcardDeck.objects.get(id=deck_id)
        except FlashcardDeck.DoesNotExist:
            return Response(
                {'error': 'Deck not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        voice = request.data.get('voice', 'us_male')
        speed = request.data.get('speed', 'normal')
        
        # Queue Celery task
        task = generate_deck_audio_batch.delay(deck_id, voice, speed)
        
        return Response({
            'deck_id': deck_id,
            'deck_name': deck.name,
            'task_id': task.id,
            'voice': voice,
            'speed': speed,
            'message': 'Batch generation queued',
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get audio storage statistics.
        
        Response:
            {
                "total_files": 150,
                "total_size_bytes": 5242880,
                "total_size_mb": 5.0,
                "storage_path": "/path/to/media/flashcard_audio"
            }
        """
        tts_service = get_tts_service()
        stats = tts_service.get_storage_stats()
        
        return Response(stats, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='stream/(?P<word>[^/.]+)')
    def stream(self, request, word=None):
        """
        Stream audio file for a word.
        
        Query Parameters:
            voice: Voice identifier (default: us_male)
            speed: Speed identifier (default: normal)
        
        Response:
            Audio file (MP3) or 404 if not found
        """
        if not word:
            raise Http404("Word parameter is required")
        
        voice = request.query_params.get('voice', 'us_male')
        speed = request.query_params.get('speed', 'normal')
        
        tts_service = get_tts_service()
        
        # Map voice shorthand to full code
        voice_code = tts_service.VOICES.get(voice, tts_service.default_voice)
        
        # Get audio path
        audio_path = tts_service.get_audio_path(word, voice_code, speed)
        
        if not audio_path.exists():
            # Try to generate on-the-fly
            logger.info(f"Audio not found for '{word}', generating on-the-fly")
            audio_url = tts_service.generate_audio(word, voice, speed)
            
            if not audio_url:
                raise Http404(f"Audio not found for word '{word}'")
            
            # Get path again after generation
            audio_path = tts_service.get_audio_path(word, voice_code, speed)
        
        # Stream the file
        try:
            return FileResponse(
                open(audio_path, 'rb'),
                content_type='audio/mpeg',
                as_attachment=False,
                filename=audio_path.name
            )
        except Exception as e:
            logger.error(f"Error streaming audio: {e}")
            raise Http404(f"Error streaming audio for '{word}'")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_flashcard_audio(request, flashcard_id):
    """
    Get audio URL for a specific flashcard.
    
    Query Parameters:
        voice: Voice identifier (default: us_male)
        speed: Speed identifier (default: normal)
        generate: Auto-generate if missing (default: true)
    
    Response:
        {
            "flashcard_id": 1,
            "word": "hello",
            "audio_url": "/media/flashcard_audio/hello_us_male_normal.mp3",
            "voice": "us_male",
            "speed": "normal",
            "generated": false
        }
    """
    try:
        flashcard = Flashcard.objects.select_related('word').get(id=flashcard_id)
    except Flashcard.DoesNotExist:
        return Response(
            {'error': 'Flashcard not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    word = flashcard.word.text
    voice = request.query_params.get('voice', 'us_male')
    speed = request.query_params.get('speed', 'normal')
    auto_generate = request.query_params.get('generate', 'true').lower() == 'true'
    
    tts_service = get_tts_service()
    
    # Map voice shorthand to full code
    voice_code = tts_service.VOICES.get(voice, tts_service.default_voice)
    
    # Check if audio exists
    audio_url = tts_service.get_audio_url(word, voice_code, speed)
    generated = False
    
    if not audio_url and auto_generate:
        # Generate audio
        audio_url = tts_service.generate_audio(word, voice, speed)
        generated = True
    
    if audio_url:
        return Response({
            'flashcard_id': flashcard_id,
            'word': word,
            'audio_url': audio_url,
            'voice': voice,
            'speed': speed,
            'generated': generated,
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Audio not available and generation failed'},
            status=status.HTTP_404_NOT_FOUND
        )
