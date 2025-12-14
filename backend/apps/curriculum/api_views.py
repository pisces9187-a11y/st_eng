"""
API Views for Phoneme Audio System - Phase 1 Day 3.

Provides RESTful endpoints for phoneme audio retrieval,
quality reporting, and audio management.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404

from .models import Phoneme, AudioSource
from .services import PhonemeAudioService
from .serializers import (
    AudioSourceSerializer,
    PhonemeMinimalSerializer,
    AudioQualityReportSerializer
)


class PhonemeAudioAPIView(APIView):
    """
    Get audio for a single phoneme with smart fallback.
    
    GET /api/v1/phonemes/{phoneme_id}/audio/
    
    Query params:
    - voice_id (optional): Filter by specific voice ID
    
    Response:
    {
        "phoneme": {"id": 1, "ipa_symbol": "i:", ...},
        "audio": {...},  # Primary audio (preferred/native/TTS)
        "alternatives": [...]  # Other available audio sources
    }
    """
    permission_classes = [AllowAny]  # Public access
    
    def get(self, request, phoneme_id):
        """Get audio for phoneme with alternatives."""
        # Get phoneme
        phoneme = get_object_or_404(Phoneme, id=phoneme_id)
        
        # Get voice_id filter (optional)
        voice_id = request.query_params.get('voice_id')
        
        # Use service to get audio
        service = PhonemeAudioService()
        audio = service.get_audio_for_phoneme(
            phoneme,
            voice_id=voice_id
        )
        
        # Get alternatives (all audio sources for this phoneme)
        alternatives = AudioSource.objects.filter(
            phoneme=phoneme
        ).exclude(
            id=audio.id if audio else None
        ).select_related('cache')
        
        # Build response
        return Response({
            'phoneme': PhonemeMinimalSerializer(phoneme).data,
            'audio': AudioSourceSerializer(audio).data if audio else None,
            'alternatives': AudioSourceSerializer(alternatives, many=True).data,
            'message': None if audio else 'No audio available - generation needed'
        }, status=status.HTTP_200_OK if audio else status.HTTP_404_NOT_FOUND)


class PhonemeAudioBulkAPIView(APIView):
    """
    Get audio for multiple phonemes in single request.
    
    GET /api/v1/phonemes/audio/bulk/?ids=1,2,3,4,5
    
    Query params:
    - ids (required): Comma-separated phoneme IDs
    - voice_id (optional): Filter by voice ID
    
    Response:
    {
        "results": {
            "1": {"phoneme": {...}, "audio": {...}},
            "2": {"phoneme": {...}, "audio": {...}},
            ...
        },
        "total": 5,
        "with_audio": 4,
        "without_audio": 1
    }
    """
    permission_classes = [AllowAny]  # Public access
    
    def get(self, request):
        """Bulk retrieve audio for phonemes."""
        # Get phoneme IDs from query param
        ids_param = request.query_params.get('ids')
        if not ids_param:
            return Response(
                {'error': 'Missing required parameter: ids'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            phoneme_ids = [int(id.strip()) for id in ids_param.split(',')]
        except ValueError:
            return Response(
                {'error': 'Invalid phoneme IDs format. Use comma-separated integers.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get phonemes
        phonemes = Phoneme.objects.filter(
            id__in=phoneme_ids
        ).select_related('category')
        
        if not phonemes.exists():
            return Response(
                {'error': 'No phonemes found for provided IDs'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get voice_id filter (optional)
        voice_id = request.query_params.get('voice_id')
        
        # Use service for bulk retrieval
        service = PhonemeAudioService()
        audio_map = service.get_audio_for_phonemes_bulk(
            phonemes,
            voice_id=voice_id
        )
        
        # Build response
        results = {}
        with_audio = 0
        without_audio = 0
        
        for phoneme in phonemes:
            audio = audio_map.get(phoneme.id)
            results[str(phoneme.id)] = {
                'phoneme': PhonemeMinimalSerializer(phoneme).data,
                'audio': AudioSourceSerializer(audio).data if audio else None
            }
            
            if audio:
                with_audio += 1
            else:
                without_audio += 1
        
        return Response({
            'results': results,
            'total': len(phonemes),
            'with_audio': with_audio,
            'without_audio': without_audio
        })


class SetPreferredAudioAPIView(APIView):
    """
    Set preferred audio source for a phoneme.
    
    POST /api/v1/phonemes/{phoneme_id}/audio/set-preferred/
    
    Body:
    {
        "audio_source_id": 5
    }
    
    Response:
    {
        "success": true,
        "message": "Preferred audio set successfully",
        "phoneme": {...},
        "audio": {...}
    }
    """
    permission_classes = [IsAdminUser]  # Admin only
    
    def post(self, request, phoneme_id):
        """Set preferred audio for phoneme."""
        # Get phoneme
        phoneme = get_object_or_404(Phoneme, id=phoneme_id)
        
        # Get audio_source_id from body
        audio_source_id = request.data.get('audio_source_id')
        if not audio_source_id:
            return Response(
                {'error': 'Missing required field: audio_source_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get audio source
        try:
            audio = AudioSource.objects.get(id=audio_source_id)
        except AudioSource.DoesNotExist:
            return Response(
                {'error': 'Audio source not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate that audio belongs to this phoneme
        if audio.phoneme_id != phoneme.id:
            return Response(
                {'error': 'Audio source does not belong to this phoneme'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use service to set preferred
        service = PhonemeAudioService()
        success = service.set_preferred_audio(phoneme, audio)
        
        if success:
            return Response({
                'success': True,
                'message': 'Preferred audio set successfully',
                'phoneme': PhonemeMinimalSerializer(phoneme).data,
                'audio': AudioSourceSerializer(audio).data
            })
        else:
            return Response(
                {'error': 'Failed to set preferred audio'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AudioQualityReportAPIView(APIView):
    """
    Get audio quality report and coverage statistics.
    
    GET /api/v1/audio/quality-report/
    
    Query params:
    - category_type (optional): Filter by category (vowel/consonant/diphthong)
    
    Response:
    {
        "total_phonemes": 44,
        "phonemes_with_audio": 40,
        "phonemes_without_audio": 4,
        "coverage_percent": 90.9,
        "native_audio_count": 25,
        "tts_audio_count": 15,
        "generated_audio_count": 0,
        "avg_quality_score": 95.5,
        "cache_enabled": true,
        "by_category": {
            "vowel": {"total": 20, "with_audio": 18, "coverage": 90.0},
            ...
        }
    }
    """
    permission_classes = [AllowAny]  # Public access for metrics
    
    def get(self, request):
        """Get quality report."""
        # Get category_type filter (optional)
        category_type = request.query_params.get('category_type')
        
        # Use service to get report
        service = PhonemeAudioService()
        report = service.get_audio_quality_report()
        
        # Serialize and return
        serializer = AudioQualityReportSerializer(report)
        return Response(serializer.data)


class PhonemeAudioURLAPIView(APIView):
    """
    Get direct audio URL for a phoneme (lightweight endpoint).
    
    GET /api/v1/phonemes/{phoneme_id}/audio/url/
    
    Response:
    {
        "phoneme_id": 1,
        "ipa_symbol": "i:",
        "audio_url": "/media/phonemes/audio/2025/12/14/audio.mp3",
        "quality_score": 100
    }
    """
    permission_classes = [AllowAny]  # Public access
    
    def get(self, request, phoneme_id):
        """Get direct audio URL."""
        phoneme = get_object_or_404(Phoneme, id=phoneme_id)
        
        service = PhonemeAudioService()
        url = service.get_audio_url(phoneme)
        
        if url:
            audio = service.get_audio_for_phoneme(phoneme)
            return Response({
                'phoneme_id': phoneme.id,
                'ipa_symbol': phoneme.ipa_symbol,
                'audio_url': url,
                'quality_score': audio.get_quality_score() if audio else None
            })
        else:
            return Response(
                {
                    'phoneme_id': phoneme.id,
                    'ipa_symbol': phoneme.ipa_symbol,
                    'audio_url': None,
                    'message': 'No audio available'
                },
                status=status.HTTP_404_NOT_FOUND
            )
