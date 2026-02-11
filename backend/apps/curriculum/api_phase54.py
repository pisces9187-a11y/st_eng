"""
Phase 5.4: Personalization & Tracking API Views

Track phoneme progress, record attempts, generate custom exercises, adaptive difficulty.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Count, Q, F
from datetime import timedelta

from apps.curriculum.models import Phoneme, PhonemeAttempt, TongueTwister, MinimalPair
from apps.users.models import UserPhonemeProgress


class PhonemeProgressAPIView(APIView):
    """
    GET: Get user's progress for a specific phoneme
    POST: Record a new attempt for a phoneme
    
    Usage:
        GET /api/v1/curriculum/phoneme-progress/<phoneme_id>/
        Response: {
            "phoneme": "/θ/",
            "mastery_level": 2,
            "accuracy_rate": 75.5,
            "total_attempts": 10,
            "current_stage": "discriminating",
            "can_practice_discrimination": true,
            "can_practice_production": false,
            "recent_attempts": [...],
            "recommendations": [...]
        }
        
        POST /api/v1/curriculum/phoneme-progress/<phoneme_id>/record-attempt/
        Payload: {
            "accuracy": 85.5,
            "attempt_duration": 3.5,
            "exercise_type": "tongue_twister",
            "transcript_text": "She sells seashells",
            "target_text": "She sells sea shells",
            "phoneme_analysis": {...},
            "problem_phonemes": ["/θ/", "/ʃ/"]
        }
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, phoneme_id):
        """Get user's progress for specific phoneme"""
        phoneme = get_object_or_404(Phoneme, id=phoneme_id)
        
        # Get or create progress
        progress, created = UserPhonemeProgress.objects.get_or_create(
            user=request.user,
            phoneme=phoneme
        )
        
        # Get recent attempts (last 10)
        recent_attempts = PhonemeAttempt.objects.filter(
            user=request.user,
            phoneme=phoneme
        ).order_by('-attempted_at')[:10]
        
        # Serialize attempts
        attempts_data = [{
            'id': attempt.id,
            'accuracy': attempt.accuracy,
            'exercise_type': attempt.exercise_type,
            'attempted_at': attempt.attempted_at.isoformat(),
            'grade': attempt.get_grade(),
            'duration': attempt.get_duration_text()
        } for attempt in recent_attempts]
        
        # Get statistics
        all_attempts = PhonemeAttempt.objects.filter(
            user=request.user,
            phoneme=phoneme
        )
        
        stats = all_attempts.aggregate(
            total=Count('id'),
            avg_accuracy=Avg('accuracy'),
            successful=Count('id', filter=Q(accuracy__gte=70))
        )
        
        return Response({
            'phoneme': {
                'id': phoneme.id,
                'ipa_symbol': phoneme.ipa_symbol,
                'vietnamese_approx': phoneme.vietnamese_approx,
                'category': phoneme.category.name_vi if phoneme.category else None
            },
            'progress': {
                'mastery_level': progress.mastery_level,
                'current_stage': progress.current_stage,
                'accuracy_rate': progress.accuracy_rate,
                'times_practiced': progress.times_practiced,
                'times_correct': progress.times_correct,
                'last_practiced_at': progress.last_practiced_at.isoformat() if progress.last_practiced_at else None,
                'can_practice_discrimination': progress.can_practice_discrimination(),
                'can_practice_production': progress.can_practice_production()
            },
            'statistics': {
                'total_attempts': stats['total'] or 0,
                'average_accuracy': round(stats['avg_accuracy'] or 0, 2),
                'successful_attempts': stats['successful'] or 0,
                'success_rate': round((stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0, 2)
            },
            'recent_attempts': attempts_data
        })
    
    def post(self, request, phoneme_id):
        """Record a new attempt"""
        phoneme = get_object_or_404(Phoneme, id=phoneme_id)
        
        # Validate required fields
        accuracy = request.data.get('accuracy')
        if accuracy is None:
            return Response(
                {'error': 'accuracy field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            accuracy = float(accuracy)
            if not 0 <= accuracy <= 100:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'accuracy must be a number between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create attempt
        attempt = PhonemeAttempt.objects.create(
            user=request.user,
            phoneme=phoneme,
            accuracy=accuracy,
            attempt_duration=float(request.data.get('attempt_duration', 0)),
            exercise_type=request.data.get('exercise_type', ''),
            transcript_text=request.data.get('transcript_text', ''),
            target_text=request.data.get('target_text', ''),
            phoneme_analysis=request.data.get('phoneme_analysis', {}),
            problem_phonemes=request.data.get('problem_phonemes', []),
            pronunciation_score=float(request.data.get('pronunciation_score', 0)),
            fluency_score=float(request.data.get('fluency_score', 0)),
            completeness_score=float(request.data.get('completeness_score', 0)),
            ai_feedback=request.data.get('ai_feedback', '')
        )
        
        # Update UserPhonemeProgress
        progress, created = UserPhonemeProgress.objects.get_or_create(
            user=request.user,
            phoneme=phoneme
        )
        
        # Update progress statistics
        is_correct = 1 if accuracy >= 70 else 0
        progress.update_progress(correct_count=is_correct, total_count=1)
        
        return Response({
            'success': True,
            'attempt': {
                'id': attempt.id,
                'accuracy': attempt.accuracy,
                'grade': attempt.get_grade(),
                'was_successful': attempt.was_successful()
            },
            'progress': {
                'mastery_level': progress.mastery_level,
                'accuracy_rate': progress.accuracy_rate,
                'times_practiced': progress.times_practiced
            }
        }, status=status.HTTP_201_CREATED)


class PhonemeProgressDashboardAPIView(APIView):
    """
    GET: Get overall phoneme progress dashboard for user
    
    Returns:
        - All phonemes with progress
        - Strongest/weakest phonemes
        - Recent activity
        - Practice recommendations
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get all user's phoneme progress
        all_progress = UserPhonemeProgress.objects.filter(
            user=request.user
        ).select_related('phoneme', 'phoneme__category').order_by('-mastery_level')
        
        # Categorize by mastery level
        mastered = []
        in_progress = []
        struggling = []
        not_started = []
        
        for progress in all_progress:
            data = {
                'phoneme_id': progress.phoneme.id,
                'ipa_symbol': progress.phoneme.ipa_symbol,
                'vietnamese_approx': progress.phoneme.vietnamese_approx,
                'category': progress.phoneme.category.name_vi if progress.phoneme.category else None,
                'mastery_level': progress.mastery_level,
                'accuracy_rate': progress.accuracy_rate,
                'times_practiced': progress.times_practiced,
                'last_practiced_at': progress.last_practiced_at.isoformat() if progress.last_practiced_at else None
            }
            
            if progress.mastery_level >= 4:
                mastered.append(data)
            elif progress.mastery_level >= 2:
                in_progress.append(data)
            elif progress.mastery_level >= 1:
                struggling.append(data)
            else:
                not_started.append(data)
        
        # Get recent attempts (last 20)
        recent_attempts = PhonemeAttempt.objects.filter(
            user=request.user
        ).select_related('phoneme').order_by('-attempted_at')[:20]
        
        attempts_data = [{
            'id': attempt.id,
            'phoneme': attempt.phoneme.ipa_symbol,
            'phoneme_id': attempt.phoneme.id,
            'accuracy': attempt.accuracy,
            'exercise_type': attempt.exercise_type,
            'attempted_at': attempt.attempted_at.isoformat(),
            'grade': attempt.get_grade()
        } for attempt in recent_attempts]
        
        # Calculate statistics
        total_phonemes = Phoneme.objects.filter(is_active=True).count()
        practiced_phonemes = all_progress.count()
        
        stats = {
            'total_phonemes': total_phonemes,
            'practiced_phonemes': practiced_phonemes,
            'mastered_phonemes': len(mastered),
            'in_progress_phonemes': len(in_progress),
            'not_started_phonemes': total_phonemes - practiced_phonemes,
            'overall_accuracy': round(
                all_progress.aggregate(avg=Avg('accuracy_rate'))['avg'] or 0,
                2
            )
        }
        
        return Response({
            'statistics': stats,
            'phonemes': {
                'mastered': mastered[:10],  # Top 10
                'in_progress': in_progress[:10],
                'struggling': struggling[:10],
                'not_started': not_started[:10]
            },
            'recent_activity': attempts_data
        })


class CustomExerciseGeneratorAPIView(APIView):
    """
    POST: Generate custom exercises based on weak phonemes
    
    Payload: {
        "phoneme_ids": [1, 2, 3],  # Optional, or auto-detect weak phonemes
        "count": 5,
        "difficulty": "medium"  # easy, medium, hard
    }
    
    Returns: List of tongue twisters and minimal pairs
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        phoneme_ids = request.data.get('phoneme_ids', [])
        count = int(request.data.get('count', 5))
        difficulty = request.data.get('difficulty', 'medium')
        
        # If no phonemes specified, find weakest phonemes
        if not phoneme_ids:
            weak_progress = UserPhonemeProgress.objects.filter(
                user=request.user,
                mastery_level__lt=3,  # Below "good" level
                accuracy_rate__lt=70
            ).order_by('accuracy_rate')[:5]
            
            phoneme_ids = [p.phoneme.id for p in weak_progress]
        
        if not phoneme_ids:
            return Response({
                'exercises': [],
                'message': 'No weak phonemes found. Great job!'
            })
        
        # Map difficulty to numbers
        difficulty_map = {
            'easy': (1, 2),
            'medium': (3, 3),
            'hard': (4, 5)
        }
        min_diff, max_diff = difficulty_map.get(difficulty, (3, 3))
        
        # Get tongue twisters
        twisters = list(TongueTwister.objects.filter(
            phoneme_id__in=phoneme_ids,
            difficulty__gte=min_diff,
            difficulty__lte=max_diff,
            is_active=True
        )[:count//2])
        
        # Get minimal pairs
        pairs = list(MinimalPair.objects.filter(
            Q(phoneme_1_id__in=phoneme_ids) | Q(phoneme_2_id__in=phoneme_ids),
            difficulty__gte=min_diff,
            difficulty__lte=max_diff
        )[:count//2])
        
        # Serialize exercises
        exercises = []
        
        for twister in twisters:
            exercises.append({
                'type': 'tongue_twister',
                'id': twister.id,
                'text': twister.text,
                'phoneme': twister.phoneme.ipa_symbol if twister.phoneme else None,
                'difficulty': twister.difficulty,
                'ipa_transcription': twister.ipa_transcription,
                'meaning_vi': twister.meaning_vi
            })
        
        for pair in pairs:
            exercises.append({
                'type': 'minimal_pair',
                'id': pair.id,
                'word_1': pair.word_1,
                'word_2': pair.word_2,
                'phoneme_1': pair.phoneme_1.ipa_symbol,
                'phoneme_2': pair.phoneme_2.ipa_symbol,
                'difficulty': pair.difficulty
            })
        
        return Response({
            'exercises': exercises,
            'target_phonemes': [
                Phoneme.objects.get(id=pid).ipa_symbol 
                for pid in phoneme_ids
            ]
        })


class ProgressHistoryAPIView(APIView):
    """
    GET: Get progress history for visualization (charts)
    
    Query params:
        - phoneme_id: specific phoneme (optional)
        - days: number of days (default 30)
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        phoneme_id = request.query_params.get('phoneme_id')
        days = int(request.query_params.get('days', 30))
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter attempts
        attempts = PhonemeAttempt.objects.filter(
            user=request.user,
            attempted_at__gte=start_date,
            attempted_at__lte=end_date
        ).order_by('attempted_at')
        
        if phoneme_id:
            attempts = attempts.filter(phoneme_id=phoneme_id)
        
        # Group by date
        daily_data = {}
        for attempt in attempts:
            date_key = attempt.attempted_at.date().isoformat()
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'date': date_key,
                    'attempts': 0,
                    'total_accuracy': 0,
                    'avg_accuracy': 0,
                    'successful_attempts': 0
                }
            
            daily_data[date_key]['attempts'] += 1
            daily_data[date_key]['total_accuracy'] += attempt.accuracy
            if attempt.accuracy >= 70:
                daily_data[date_key]['successful_attempts'] += 1
        
        # Calculate averages
        for data in daily_data.values():
            data['avg_accuracy'] = round(data['total_accuracy'] / data['attempts'], 2)
            del data['total_accuracy']  # Remove intermediate calculation
        
        # Convert to list sorted by date
        history = sorted(daily_data.values(), key=lambda x: x['date'])
        
        return Response({
            'history': history,
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            }
        })


class AdaptiveDifficultyAPIView(APIView):
    """
    GET: Get recommended difficulty level for a phoneme
    
    Based on recent performance, suggests difficulty adjustment
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, phoneme_id):
        phoneme = get_object_or_404(Phoneme, id=phoneme_id)
        
        # Get progress
        try:
            progress = UserPhonemeProgress.objects.get(
                user=request.user,
                phoneme=phoneme
            )
        except UserPhonemeProgress.DoesNotExist:
            return Response({
                'recommended_difficulty': 'easy',
                'reason': 'First time practicing this phoneme'
            })
        
        # Get recent attempts (last 5)
        recent_attempts = PhonemeAttempt.objects.filter(
            user=request.user,
            phoneme=phoneme
        ).order_by('-attempted_at')[:5]
        
        if not recent_attempts.exists():
            return Response({
                'recommended_difficulty': 'easy',
                'reason': 'No recent attempts found'
            })
        
        # Calculate recent average
        recent_avg = sum(a.accuracy for a in recent_attempts) / len(recent_attempts)
        
        # Determine difficulty
        if recent_avg >= 90:
            difficulty = 'hard'
            reason = 'Excellent performance! Ready for advanced challenges.'
        elif recent_avg >= 75:
            difficulty = 'medium'
            reason = 'Good progress. Continue with moderate difficulty.'
        else:
            difficulty = 'easy'
            reason = 'Keep practicing basics to build confidence.'
        
        return Response({
            'recommended_difficulty': difficulty,
            'reason': reason,
            'recent_average': round(recent_avg, 2),
            'mastery_level': progress.mastery_level,
            'total_attempts': progress.times_practiced
        })
