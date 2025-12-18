"""
Learning Hub Dashboard API for Day 10.

Endpoints:
- GET /api/v1/dashboard/stats/ - Overall statistics (30 days)
- GET /api/v1/dashboard/recommendations/ - Top 3 weakest phonemes to practice
- GET /api/v1/dashboard/activity/ - Recent activity feed
- GET /api/v1/dashboard/progress-chart/ - Progress data for Chart.js
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q, F
from django.utils.timezone import now
from datetime import timedelta

from apps.study.models import DiscriminationSession, DiscriminationAttempt, ProductionRecording
from apps.users.models import UserPhonemeProgress
from apps.curriculum.models import Phoneme


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """
    Get overall dashboard statistics for the last 30 days.
    
    GET /api/v1/dashboard/stats/
    
    Returns:
    - total_practice_time: Total minutes practiced
    - discrimination_stats: Quiz statistics
    - production_stats: Recording statistics
    - phoneme_progress: Phoneme mastery stats
    - streak_info: Practice streak data
    """
    user = request.user
    thirty_days_ago = now() - timedelta(days=30)
    
    # ===== Discrimination Stats =====
    discrimination_sessions = DiscriminationSession.objects.filter(
        user=user,
        created_at__gte=thirty_days_ago
    )
    
    completed_sessions = discrimination_sessions.filter(status='completed')
    
    discrimination_stats = {
        'total_sessions': completed_sessions.count(),
        'total_questions': completed_sessions.aggregate(
            total=Sum('total_questions')
        )['total'] or 0,
        'correct_answers': completed_sessions.aggregate(
            total=Sum('correct_answers')
        )['total'] or 0,
        'avg_accuracy': completed_sessions.aggregate(
            avg=Avg('accuracy')
        )['avg'] or 0,
        'best_accuracy': completed_sessions.aggregate(
            best=Avg('accuracy')
        )['best'] or 0,
        'total_time_seconds': sum([
            (session.completed_at - session.started_at).total_seconds()
            for session in completed_sessions
            if session.completed_at
        ])
    }
    
    # ===== Production Stats =====
    production_recordings = ProductionRecording.objects.filter(
        user=user,
        created_at__gte=thirty_days_ago
    )
    
    production_stats = {
        'total_recordings': production_recordings.count(),
        'unique_phonemes': production_recordings.values('phoneme').distinct().count(),
        'avg_score': production_recordings.filter(
            self_assessment_score__isnull=False
        ).aggregate(avg=Avg('self_assessment_score'))['avg'] or 0,
        'total_duration_seconds': production_recordings.aggregate(
            total=Sum('duration_seconds')
        )['total'] or 0,
        'best_recordings': production_recordings.filter(is_best=True).count()
    }
    
    # ===== Phoneme Progress =====
    phoneme_progress = UserPhonemeProgress.objects.filter(user=user)
    
    phoneme_stats = {
        'total_phonemes': Phoneme.objects.filter(is_active=True).count(),
        'practiced_phonemes': phoneme_progress.count(),
        'mastered_phonemes': phoneme_progress.filter(
            discrimination_accuracy__gte=80,
            production_practice_count__gte=5
        ).count(),
        'avg_discrimination_accuracy': phoneme_progress.aggregate(
            avg=Avg('discrimination_accuracy')
        )['avg'] or 0,
        'avg_production_count': phoneme_progress.aggregate(
            avg=Avg('production_practice_count')
        )['avg'] or 0
    }
    
    # ===== Total Practice Time =====
    total_practice_minutes = (
        discrimination_stats['total_time_seconds'] +
        production_stats['total_duration_seconds']
    ) / 60
    
    # ===== Achievements =====
    achievements = {
        'first_quiz': discrimination_stats['total_sessions'] >= 1,
        'first_recording': production_stats['total_recordings'] >= 1,
        'perfect_quiz': completed_sessions.filter(accuracy=100).exists(),
        'practice_streak_7': total_practice_minutes >= 7 * 10,  # 10 min/day for 7 days
        'phoneme_master_10': phoneme_stats['mastered_phonemes'] >= 10,
    }
    
    return Response({
        'success': True,
        'data': {
            'total_practice_minutes': round(total_practice_minutes, 1),
            'discrimination': discrimination_stats,
            'production': production_stats,
            'phoneme_progress': phoneme_stats,
            'achievements': achievements,
            'period': '30 days'
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """
    Get top 3 weakest phonemes to practice.
    
    GET /api/v1/dashboard/recommendations/
    
    Algorithm:
    1. Find phonemes with discrimination accuracy < 75%
    2. Sort by accuracy (ascending) and practice count (ascending)
    3. Return top 3 with practice suggestions
    
    Returns:
    - recommendations: List of 3 phonemes with reasons
    """
    user = request.user
    
    # Get all phoneme progress, ordered by weakness
    weak_phonemes = UserPhonemeProgress.objects.filter(
        user=user
    ).select_related('phoneme').order_by(
        'discrimination_accuracy',
        'production_practice_count'
    )[:3]
    
    # If less than 3, get unpracticed phonemes
    if weak_phonemes.count() < 3:
        practiced_ids = UserPhonemeProgress.objects.filter(
            user=user
        ).values_list('phoneme_id', flat=True)
        
        unpracticed = Phoneme.objects.filter(
            is_active=True
        ).exclude(id__in=practiced_ids)[:3 - weak_phonemes.count()]
        
        # Combine
        recommendations = []
        
        # Add weak phonemes
        for progress in weak_phonemes:
            reason = []
            if progress.discrimination_accuracy < 75:
                reason.append(f'Độ chính xác phân biệt thấp ({progress.discrimination_accuracy:.0f}%)')
            if progress.production_practice_count < 5:
                reason.append(f'Ít bản ghi ({progress.production_practice_count})')
            
            recommendations.append({
                'phoneme': {
                    'id': progress.phoneme.id,
                    'ipa_symbol': progress.phoneme.ipa_symbol,
                    'name_vi': progress.phoneme.name_vi,
                    'description_vi': progress.phoneme.description_vi
                },
                'reason': ' • '.join(reason) if reason else 'Cần luyện thêm',
                'discrimination_accuracy': progress.discrimination_accuracy,
                'production_count': progress.production_practice_count,
                'priority': 'high' if progress.discrimination_accuracy < 60 else 'medium'
            })
        
        # Add unpracticed
        for phoneme in unpracticed:
            recommendations.append({
                'phoneme': {
                    'id': phoneme.id,
                    'ipa_symbol': phoneme.ipa_symbol,
                    'name_vi': phoneme.name_vi,
                    'description_vi': phoneme.description_vi
                },
                'reason': 'Chưa luyện tập',
                'discrimination_accuracy': 0,
                'production_count': 0,
                'priority': 'low'
            })
    else:
        recommendations = []
        for progress in weak_phonemes:
            reason = []
            if progress.discrimination_accuracy < 75:
                reason.append(f'Độ chính xác {progress.discrimination_accuracy:.0f}%')
            if progress.production_practice_count < 5:
                reason.append(f'{progress.production_practice_count} bản ghi')
            
            recommendations.append({
                'phoneme': {
                    'id': progress.phoneme.id,
                    'ipa_symbol': progress.phoneme.ipa_symbol,
                    'name_vi': progress.phoneme.name_vi,
                    'description_vi': progress.phoneme.description_vi
                },
                'reason': ' • '.join(reason) if reason else 'Cần luyện thêm',
                'discrimination_accuracy': progress.discrimination_accuracy,
                'production_count': progress.production_practice_count,
                'priority': 'high' if progress.discrimination_accuracy < 60 else 'medium'
            })
    
    return Response({
        'success': True,
        'data': {
            'recommendations': recommendations[:3],
            'total_weak_phonemes': weak_phonemes.count()
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_activity(request):
    """
    Get recent activity feed (last 20 activities).
    
    GET /api/v1/dashboard/activity/
    
    Query params:
    - limit (int): Number of activities (default 20)
    
    Returns:
    - activities: Combined list of discrimination and production activities
    """
    user = request.user
    limit = int(request.query_params.get('limit', 20))
    
    activities = []
    
    # Get recent discrimination sessions
    recent_sessions = DiscriminationSession.objects.filter(
        user=user,
        status='completed'
    ).order_by('-completed_at')[:limit]
    
    for session in recent_sessions:
        activities.append({
            'type': 'discrimination',
            'icon': '🎯',
            'title': 'Hoàn thành Quiz Phân biệt',
            'description': f'Đạt {session.accuracy:.0f}% độ chính xác ({session.correct_answers}/{session.total_questions} câu đúng)',
            'timestamp': session.completed_at.isoformat() if session.completed_at else session.created_at.isoformat(),
            'accuracy': session.accuracy,
            'details': {
                'session_id': session.session_id,
                'correct': session.correct_answers,
                'total': session.total_questions
            }
        })
    
    # Get recent production recordings
    recent_recordings = ProductionRecording.objects.filter(
        user=user
    ).select_related('phoneme').order_by('-created_at')[:limit]
    
    for recording in recent_recordings:
        stars = '⭐' * (recording.self_assessment_score or 0)
        activities.append({
            'type': 'production',
            'icon': '🎤',
            'title': f'Ghi âm /{recording.phoneme.ipa_symbol}/',
            'description': f'{recording.phoneme.name_vi} • {stars}' if recording.self_assessment_score else recording.phoneme.name_vi,
            'timestamp': recording.created_at.isoformat(),
            'score': recording.self_assessment_score,
            'details': {
                'phoneme_id': recording.phoneme.id,
                'phoneme_symbol': recording.phoneme.ipa_symbol,
                'is_best': recording.is_best
            }
        })
    
    # Sort by timestamp (descending)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Limit to requested amount
    activities = activities[:limit]
    
    return Response({
        'success': True,
        'data': {
            'activities': activities,
            'total': len(activities)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_progress_chart_data(request):
    """
    Get progress data for Chart.js visualization.
    
    GET /api/v1/dashboard/progress-chart/
    
    Query params:
    - period (str): '7days', '30days', '90days' (default: 30days)
    
    Returns:
    - labels: Date labels for X-axis
    - discrimination_data: Daily discrimination accuracy
    - production_data: Daily recording counts
    """
    user = request.user
    period = request.query_params.get('period', '30days')
    
    # Determine date range
    if period == '7days':
        days = 7
    elif period == '90days':
        days = 90
    else:
        days = 30
    
    start_date = now() - timedelta(days=days)
    
    # Generate date labels
    labels = []
    discrimination_data = []
    production_data = []
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        labels.append(date.strftime('%m/%d'))
        
        # Discrimination accuracy for this day
        day_sessions = DiscriminationSession.objects.filter(
            user=user,
            status='completed',
            completed_at__gte=date,
            completed_at__lt=next_date
        )
        
        avg_accuracy = day_sessions.aggregate(avg=Avg('accuracy'))['avg']
        discrimination_data.append(round(avg_accuracy, 1) if avg_accuracy else 0)
        
        # Production recordings for this day
        day_recordings = ProductionRecording.objects.filter(
            user=user,
            created_at__gte=date,
            created_at__lt=next_date
        ).count()
        
        production_data.append(day_recordings)
    
    return Response({
        'success': True,
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Độ chính xác Quiz (%)',
                    'data': discrimination_data,
                    'borderColor': '#F47C26',
                    'backgroundColor': 'rgba(244, 124, 38, 0.1)',
                    'tension': 0.4,
                    'yAxisID': 'y'
                },
                {
                    'label': 'Số bản ghi',
                    'data': production_data,
                    'borderColor': '#667eea',
                    'backgroundColor': 'rgba(102, 126, 234, 0.1)',
                    'tension': 0.4,
                    'yAxisID': 'y1'
                }
            ],
            'period': period
        }
    })
