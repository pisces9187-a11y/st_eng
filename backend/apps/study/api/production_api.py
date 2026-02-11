"""
Production Recording API for Day 8-9.

Endpoints:
- POST   /api/v1/production/recordings/upload/ - Upload new recording
- GET    /api/v1/production/recordings/ - List user's recordings
- GET    /api/v1/production/recordings/<id>/ - Get recording detail
- PATCH  /api/v1/production/recordings/<id>/ - Update recording (rating, mark as best)
- DELETE /api/v1/production/recordings/<id>/ - Delete recording
"""

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Max
from django.core.files.base import ContentFile
import os
import uuid

from ..models import ProductionRecording
from apps.curriculum.models import Phoneme


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_recording(request):
    """
    Upload a new pronunciation recording.
    
    POST /api/v1/production/recordings/upload/
    
    Form Data:
    - phoneme_id (int): Phoneme being practiced
    - audio_file (file): Audio recording (MP3, WAV, WebM)
    - duration_seconds (float): Recording duration
    - self_assessment_score (int, optional): 1-5 stars
    
    Returns:
    - recording: Created recording object
    """
    user = request.user
    
    # Validate required fields
    phoneme_id = request.data.get('phoneme_id')
    audio_file = request.FILES.get('audio_file')
    duration_seconds = request.data.get('duration_seconds')
    
    if not phoneme_id:
        return Response({
            'success': False,
            'error': 'phoneme_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not audio_file:
        return Response({
            'success': False,
            'error': 'audio_file is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate phoneme exists
    try:
        phoneme = Phoneme.objects.get(id=phoneme_id)
    except Phoneme.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Phoneme not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Validate file size (max 10MB)
    if audio_file.size > 10 * 1024 * 1024:
        return Response({
            'success': False,
            'error': 'File size must be less than 10MB'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file type
    allowed_extensions = ['.mp3', '.wav', '.webm', '.ogg', '.m4a']
    file_ext = os.path.splitext(audio_file.name)[1].lower()
    if file_ext not in allowed_extensions:
        return Response({
            'success': False,
            'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Parse duration
    try:
        duration = float(duration_seconds) if duration_seconds else 0.0
    except (ValueError, TypeError):
        duration = 0.0
    
    # Parse self-assessment score
    self_assessment_score = request.data.get('self_assessment_score')
    if self_assessment_score:
        try:
            self_assessment_score = int(self_assessment_score)
            if self_assessment_score < 1 or self_assessment_score > 5:
                self_assessment_score = None
        except (ValueError, TypeError):
            self_assessment_score = None
    
    # Create recording
    recording = ProductionRecording.objects.create(
        user=user,
        phoneme=phoneme,
        recording_file=audio_file,
        duration_seconds=duration,
        file_size_bytes=audio_file.size,
        self_assessment_score=self_assessment_score,
        is_best=False  # Will be updated if user marks it later
    )
    
    # Update user progress
    from apps.users.models import UserPhonemeProgress
    progress, created = UserPhonemeProgress.objects.get_or_create(
        user=user,
        phoneme=phoneme,
        defaults={
            'production_practiced': True,
            'production_practice_count': 1,
            'last_production_practice': recording.created_at
        }
    )
    
    if not created:
        progress.production_practiced = True
        progress.production_practice_count += 1
        progress.last_production_practice = recording.created_at
        progress.save(update_fields=[
            'production_practiced',
            'production_practice_count',
            'last_production_practice'
        ])
    
    return Response({
        'success': True,
        'message': 'Recording uploaded successfully',
        'data': {
            'recording': {
                'id': recording.id,
                'phoneme': {
                    'id': phoneme.id,
                    'ipa_symbol': phoneme.ipa_symbol,
                    'name_vi': phoneme.name_vi
                },
                'recording_url': request.build_absolute_uri(recording.recording_file.url),
                'duration_seconds': recording.duration_seconds,
                'file_size_bytes': recording.file_size_bytes,
                'self_assessment_score': recording.self_assessment_score,
                'is_best': recording.is_best,
                'created_at': recording.created_at.isoformat(),
            },
            'progress': {
                'practice_count': progress.production_practice_count,
                'last_practice': progress.last_production_practice.isoformat()
            }
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_recordings(request):
    """
    List user's production recordings.
    
    GET /api/v1/production/recordings/
    
    Query Params:
    - phoneme_id (int, optional): Filter by phoneme
    - is_best (bool, optional): Filter by best recordings only
    - limit (int, optional): Pagination limit (default: 20)
    - offset (int, optional): Pagination offset (default: 0)
    
    Returns:
    - recordings: List of recording objects
    - total: Total count
    - stats: Overall statistics
    """
    user = request.user
    
    # Base queryset
    queryset = ProductionRecording.objects.filter(user=user).select_related('phoneme')
    
    # Filters
    phoneme_id = request.query_params.get('phoneme_id')
    if phoneme_id:
        queryset = queryset.filter(phoneme_id=phoneme_id)
    
    is_best = request.query_params.get('is_best')
    if is_best and is_best.lower() == 'true':
        queryset = queryset.filter(is_best=True)
    
    # Stats
    total_recordings = queryset.count()
    avg_duration = queryset.aggregate(Avg('duration_seconds'))['duration_seconds__avg'] or 0
    avg_score = queryset.filter(
        self_assessment_score__isnull=False
    ).aggregate(Avg('self_assessment_score'))['self_assessment_score__avg'] or 0
    
    # Pagination
    try:
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
    except ValueError:
        limit = 20
        offset = 0
    
    # Order by created_at desc
    recordings = queryset.order_by('-created_at')[offset:offset + limit]
    
    # Serialize
    recordings_data = []
    for recording in recordings:
        recordings_data.append({
            'id': recording.id,
            'phoneme': {
                'id': recording.phoneme.id,
                'ipa_symbol': recording.phoneme.ipa_symbol,
                'name_vi': recording.phoneme.name_vi
            },
            'recording_url': request.build_absolute_uri(recording.recording_file.url),
            'duration_seconds': recording.duration_seconds,
            'file_size_bytes': recording.file_size_bytes,
            'self_assessment_score': recording.self_assessment_score,
            'is_best': recording.is_best,
            'created_at': recording.created_at.isoformat(),
        })
    
    return Response({
        'success': True,
        'data': {
            'recordings': recordings_data,
            'total': total_recordings,
            'stats': {
                'total_recordings': total_recordings,
                'avg_duration': round(avg_duration, 2),
                'avg_score': round(avg_score, 2)
            }
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recording_detail(request, recording_id):
    """
    Get single recording detail.
    
    GET /api/v1/production/recordings/<id>/
    
    Returns:
    - recording: Recording object with full details
    """
    user = request.user
    
    recording = get_object_or_404(
        ProductionRecording.objects.select_related('phoneme'),
        id=recording_id,
        user=user
    )
    
    return Response({
        'success': True,
        'data': {
            'recording': {
                'id': recording.id,
                'phoneme': {
                    'id': recording.phoneme.id,
                    'ipa_symbol': recording.phoneme.ipa_symbol,
                    'name_vi': recording.phoneme.name_vi,
                    'name': recording.phoneme.name,
                    'description_vi': recording.phoneme.description_vi
                },
                'recording_url': request.build_absolute_uri(recording.recording_file.url),
                'duration_seconds': recording.duration_seconds,
                'file_size_bytes': recording.file_size_bytes,
                'self_assessment_score': recording.self_assessment_score,
                'ai_score': recording.ai_score,
                'is_best': recording.is_best,
                'created_at': recording.created_at.isoformat(),
                'updated_at': recording.updated_at.isoformat(),
            }
        }
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_recording(request, recording_id):
    """
    Update recording (self-assessment score or mark as best).
    
    PATCH /api/v1/production/recordings/<id>/
    
    Body:
    - self_assessment_score (int, optional): 1-5 stars
    - is_best (bool, optional): Mark as best recording
    
    Returns:
    - recording: Updated recording object
    """
    user = request.user
    
    recording = get_object_or_404(
        ProductionRecording,
        id=recording_id,
        user=user
    )
    
    # Update self-assessment score
    if 'self_assessment_score' in request.data:
        score = request.data['self_assessment_score']
        if score is None:
            recording.self_assessment_score = None
        else:
            try:
                score = int(score)
                if 1 <= score <= 5:
                    recording.self_assessment_score = score
                else:
                    return Response({
                        'success': False,
                        'error': 'self_assessment_score must be between 1 and 5'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'self_assessment_score must be an integer'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update is_best
    if 'is_best' in request.data:
        is_best = request.data['is_best']
        if isinstance(is_best, bool) or isinstance(is_best, str):
            is_best = str(is_best).lower() == 'true'
            recording.is_best = is_best
    
    recording.save()
    
    return Response({
        'success': True,
        'message': 'Recording updated successfully',
        'data': {
            'recording': {
                'id': recording.id,
                'self_assessment_score': recording.self_assessment_score,
                'is_best': recording.is_best,
                'updated_at': recording.updated_at.isoformat(),
            }
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_recording(request, recording_id):
    """
    Delete a recording.
    
    DELETE /api/v1/production/recordings/<id>/
    
    Returns:
    - success: True if deleted
    """
    user = request.user
    
    recording = get_object_or_404(
        ProductionRecording,
        id=recording_id,
        user=user
    )
    
    # Delete file from storage
    if recording.recording_file:
        recording.recording_file.delete(save=False)
    
    recording.delete()
    
    return Response({
        'success': True,
        'message': 'Recording deleted successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_phoneme_recordings(request, phoneme_id):
    """
    Get all recordings for a specific phoneme.
    
    GET /api/v1/production/phonemes/<id>/recordings/
    
    Returns:
    - recordings: List of recordings for this phoneme
    - phoneme: Phoneme details
    - stats: Statistics for this phoneme
    """
    user = request.user
    
    # Validate phoneme exists
    phoneme = get_object_or_404(Phoneme, id=phoneme_id)
    
    # Get recordings
    recordings = ProductionRecording.objects.filter(
        user=user,
        phoneme=phoneme
    ).order_by('-created_at')
    
    # Stats
    total_recordings = recordings.count()
    avg_score = recordings.filter(
        self_assessment_score__isnull=False
    ).aggregate(Avg('self_assessment_score'))['self_assessment_score__avg'] or 0
    best_recording = recordings.filter(is_best=True).first()
    
    # Serialize
    recordings_data = []
    for recording in recordings:
        recordings_data.append({
            'id': recording.id,
            'recording_url': request.build_absolute_uri(recording.recording_file.url),
            'duration_seconds': recording.duration_seconds,
            'self_assessment_score': recording.self_assessment_score,
            'is_best': recording.is_best,
            'created_at': recording.created_at.isoformat(),
        })
    
    return Response({
        'success': True,
        'data': {
            'phoneme': {
                'id': phoneme.id,
                'ipa_symbol': phoneme.ipa_symbol,
                'name_vi': phoneme.name_vi,
                'name': phoneme.name,
                'description_vi': phoneme.description_vi
            },
            'recordings': recordings_data,
            'stats': {
                'total_recordings': total_recordings,
                'avg_score': round(avg_score, 2),
                'has_best': best_recording is not None
            }
        }
    })
