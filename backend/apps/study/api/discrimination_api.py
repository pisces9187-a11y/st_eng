"""
API views for Discrimination Practice (Days 6-7).
Handles quiz session creation, answer submission, and results.
"""

import uuid
import random
from datetime import timedelta

from django.utils import timezone
from django.db.models import Avg, Count, F
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.curriculum.models import MinimalPair, Phoneme
from apps.users.models import UserPhonemeProgress
from ..models import DiscriminationSession, DiscriminationAttempt


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request):
    """
    Start a new discrimination quiz session.
    Generates 10 random questions from minimal pairs.
    
    POST /api/v1/discrimination/sessions/start/
    Response: {session_id, total_questions, time_limit, questions[]}
    """
    user = request.user
    
    # Create session with UUID
    session_id = str(uuid.uuid4())
    session = DiscriminationSession.objects.create(
        user=user,
        session_id=session_id,
        total_questions=10,
        time_limit_seconds=300  # 5 minutes
    )
    
    # Get random minimal pairs (prefer user's weak phonemes)
    minimal_pairs = MinimalPair.objects.filter(
        word_1_audio__isnull=False,
        word_2_audio__isnull=False
    ).select_related('phoneme_1', 'phoneme_2')
    
    # Prefer pairs with low user accuracy
    user_progress = UserPhonemeProgress.objects.filter(
        user=user,
        discrimination_accuracy__lt=75.0
    ).values_list('phoneme_id', flat=True)
    
    if user_progress:
        # Prioritize weak phonemes
        weak_pairs = minimal_pairs.filter(
            phoneme_1__in=user_progress
        ) | minimal_pairs.filter(
            phoneme_2__in=user_progress
        )
        if weak_pairs.count() >= 10:
            minimal_pairs = weak_pairs
    
    # Sample 10 random pairs
    selected_pairs = list(minimal_pairs.order_by('?')[:10])
    
    if len(selected_pairs) < 10:
        return Response({
            'success': False,
            'error': 'Not enough minimal pairs with audio available'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Build question list
    questions = []
    question_cache = {}  # Store correct answers for validation later
    
    for idx, pair in enumerate(selected_pairs, 1):
        # Randomly choose which word is correct
        correct_word = random.choice(['word_1', 'word_2'])
        
        # Cache the correct answer (store in session for later validation)
        question_cache[f"q{idx}_pair{pair.id}"] = correct_word
        
        question = {
            'question_number': idx,
            'minimal_pair_id': pair.id,
            'word_1': pair.word_1,
            'word_1_ipa': pair.word_1_ipa,
            'word_1_meaning': pair.word_1_meaning,
            'word_1_audio': request.build_absolute_uri(pair.word_1_audio.url) if pair.word_1_audio else None,
            'word_2': pair.word_2,
            'word_2_ipa': pair.word_2_ipa,
            'word_2_meaning': pair.word_2_meaning,
            'word_2_audio': request.build_absolute_uri(pair.word_2_audio.url) if pair.word_2_audio else None,
            'phoneme_1': {
                'id': pair.phoneme_1.id,
                'ipa_symbol': pair.phoneme_1.ipa_symbol,
                'name_vi': pair.phoneme_1.name_vi
            },
            'phoneme_2': {
                'id': pair.phoneme_2.id,
                'ipa_symbol': pair.phoneme_2.ipa_symbol,
                'name_vi': pair.phoneme_2.name_vi
            },
            'difficulty': pair.difficulty,
            'difference_note': pair.difference_note_vi or pair.difference_note
        }
        questions.append(question)
    
    # Store question cache in session notes (as JSON string)
    import json
    session.notes = json.dumps(question_cache)
    session.save(update_fields=['notes'])
    
    return Response({
        'success': True,
        'session': {
            'session_id': session_id,
            'total_questions': 10,
            'time_limit_seconds': 300,
            'started_at': session.started_at.isoformat()
        },
        'questions': questions
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_attempt(request):
    """
    Submit answer for a single question.
    Validates answer and returns immediate feedback.
    
    POST /api/v1/discrimination/attempts/submit/
    Body: {session_id, question_number, minimal_pair_id, user_answer, response_time}
    """
    user = request.user
    
    # Validate request data
    session_id = request.data.get('session_id')
    question_number = request.data.get('question_number')
    minimal_pair_id = request.data.get('minimal_pair_id')
    user_answer = request.data.get('user_answer')
    response_time = request.data.get('response_time', 0)
    
    if not all([session_id, question_number, minimal_pair_id, user_answer]):
        return Response({
            'success': False,
            'error': 'Missing required fields'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get session
    try:
        session = DiscriminationSession.objects.get(
            session_id=session_id,
            user=user,
            status='in_progress'
        )
    except DiscriminationSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found or already completed'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if time limit exceeded
    time_elapsed = timezone.now() - session.started_at
    if time_elapsed.total_seconds() > session.time_limit_seconds:
        session.status = 'expired'
        session.save()
        return Response({
            'success': False,
            'error': 'Time limit exceeded'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get minimal pair
    try:
        minimal_pair = MinimalPair.objects.get(id=minimal_pair_id)
    except MinimalPair.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Minimal pair not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get correct answer from session cache
    import json
    question_cache = json.loads(session.notes or '{}')
    cache_key = f"q{question_number}_pair{minimal_pair_id}"
    
    if cache_key not in question_cache:
        return Response({
            'error': 'Invalid question',
            'message': 'This question was not part of this session.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    correct_word = question_cache[cache_key]
    is_correct = (user_answer == correct_word)
    
    # Create attempt record
    attempt = DiscriminationAttempt.objects.create(
        user=user,
        session=session,
        minimal_pair=minimal_pair,
        question_number=question_number,
        correct_word=correct_word,
        user_answer=user_answer,
        is_correct=is_correct,
        response_time=response_time
    )
    
    # Update session stats
    if is_correct:
        session.correct_answers += 1
        session.save(update_fields=['correct_answers'])
    
    # Build feedback
    correct_word_text = minimal_pair.word_1 if correct_word == 'word_1' else minimal_pair.word_2
    correct_word_ipa = minimal_pair.word_1_ipa if correct_word == 'word_1' else minimal_pair.word_2_ipa
    
    feedback_message = "Correct! 🎉" if is_correct else "Incorrect. Keep practicing!"
    explanation = f"The correct word was '{correct_word_text}' ({correct_word_ipa})."
    if minimal_pair.difference_note_vi:
        explanation += f" {minimal_pair.difference_note_vi}"
    
    # Calculate current progress
    answered = DiscriminationAttempt.objects.filter(session=session).count()
    
    return Response({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': correct_word,
        'feedback': {
            'message': feedback_message,
            'explanation': explanation,
            'correct_word': correct_word_text,
            'correct_ipa': correct_word_ipa
        },
        'session_progress': {
            'answered': answered,
            'total': session.total_questions,
            'correct_so_far': session.correct_answers,
            'current_accuracy': (session.correct_answers / answered * 100) if answered > 0 else 0
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_session(request, session_id):
    """
    Mark session as completed and update user progress.
    
    POST /api/v1/discrimination/sessions/{session_id}/complete/
    """
    user = request.user
    
    try:
        session = DiscriminationSession.objects.get(
            session_id=session_id,
            user=user
        )
    except DiscriminationSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if session.status == 'completed':
        return Response({
            'success': False,
            'error': 'Session already completed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Complete session
    session.complete_session()
    
    # Update user phoneme progress
    attempts = DiscriminationAttempt.objects.filter(session=session).select_related('minimal_pair')
    
    phoneme_stats = {}
    for attempt in attempts:
        # Track accuracy for both phonemes in the pair
        for phoneme in [attempt.minimal_pair.phoneme_1, attempt.minimal_pair.phoneme_2]:
            if phoneme.id not in phoneme_stats:
                phoneme_stats[phoneme.id] = {'correct': 0, 'total': 0}
            phoneme_stats[phoneme.id]['total'] += 1
            if attempt.is_correct:
                phoneme_stats[phoneme.id]['correct'] += 1
    
    # Update UserPhonemeProgress
    progress_updated = []
    for phoneme_id, stats in phoneme_stats.items():
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        progress, created = UserPhonemeProgress.objects.get_or_create(
            user=user,
            phoneme_id=phoneme_id,
            defaults={'discrimination_accuracy': accuracy}
        )
        
        if not created:
            # Update with weighted average (70% old, 30% new)
            old_accuracy = progress.discrimination_accuracy
            new_accuracy = old_accuracy * 0.7 + accuracy * 0.3
            progress.discrimination_accuracy = new_accuracy
            progress.discrimination_attempts += stats['total']
            progress.save(update_fields=['discrimination_accuracy', 'discrimination_attempts'])
            
            progress_updated.append({
                'phoneme_id': phoneme_id,
                'phoneme_symbol': progress.phoneme.ipa_symbol,
                'old_accuracy': old_accuracy,
                'new_accuracy': new_accuracy
            })
    
    # Check for achievements (future feature)
    achievements_earned = []
    
    return Response({
        'success': True,
        'session': {
            'session_id': session.session_id,
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'accuracy': session.accuracy,
            'time_spent_seconds': session.time_spent_seconds,
            'completed_at': session.completed_at.isoformat()
        },
        'progress_updated': progress_updated,
        'achievements_earned': achievements_earned
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session(request, session_id):
    """
    Get session details and all attempts.
    
    GET /api/v1/discrimination/sessions/{session_id}/
    """
    user = request.user
    
    try:
        session = DiscriminationSession.objects.get(
            session_id=session_id,
            user=user
        )
    except DiscriminationSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get all attempts
    attempts = DiscriminationAttempt.objects.filter(
        session=session
    ).select_related('minimal_pair').order_by('question_number')
    
    attempts_data = []
    for attempt in attempts:
        attempts_data.append({
            'question_number': attempt.question_number,
            'minimal_pair': {
                'word_1': attempt.minimal_pair.word_1,
                'word_1_ipa': attempt.minimal_pair.word_1_ipa,
                'word_2': attempt.minimal_pair.word_2,
                'word_2_ipa': attempt.minimal_pair.word_2_ipa
            },
            'correct_word': attempt.correct_word,
            'user_answer': attempt.user_answer,
            'is_correct': attempt.is_correct,
            'response_time': attempt.response_time
        })
    
    return Response({
        'success': True,
        'session': {
            'session_id': session.session_id,
            'status': session.status,
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'accuracy': session.accuracy,
            'time_spent_seconds': session.time_spent_seconds,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        },
        'attempts': attempts_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    """
    Get user's discrimination session history.
    
    GET /api/v1/discrimination/sessions/history/?limit=10&offset=0
    """
    user = request.user
    limit = int(request.GET.get('limit', 10))
    offset = int(request.GET.get('offset', 0))
    
    sessions = DiscriminationSession.objects.filter(
        user=user,
        status='completed'
    ).order_by('-completed_at')[offset:offset+limit]
    
    total_sessions = DiscriminationSession.objects.filter(
        user=user,
        status='completed'
    ).count()
    
    sessions_data = []
    for session in sessions:
        sessions_data.append({
            'session_id': session.session_id,
            'accuracy': session.accuracy,
            'correct_answers': session.correct_answers,
            'total_questions': session.total_questions,
            'time_spent_seconds': session.time_spent_seconds,
            'completed_at': session.completed_at.isoformat()
        })
    
    return Response({
        'success': True,
        'total_sessions': total_sessions,
        'sessions': sessions_data
    })
