"""
API Views for Study app.

Handles user progress, flashcard SRS, practice sessions, and learning goals.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.curriculum.models import Course, Lesson, Flashcard, Sentence
from .models import (
    UserCourseEnrollment, UserLessonProgress, UserFlashcard,
    UserSentenceProgress, PracticeSession, PracticeResult,
    DailyStreak, LearningGoal
)
from .serializers import (
    UserCourseEnrollmentSerializer, UserCourseEnrollmentCreateSerializer,
    UserLessonProgressSerializer, UserLessonProgressUpdateSerializer,
    UserFlashcardSerializer, FlashcardReviewSerializer, FlashcardReviewBatchSerializer,
    UserSentenceProgressSerializer,
    PracticeSessionSerializer, PracticeSessionCreateSerializer, PracticeSessionUpdateSerializer,
    PracticeResultSerializer, PracticeResultCreateSerializer,
    DailyStreakSerializer, LearningGoalSerializer, LearningGoalCreateSerializer,
    StudyStatsSerializer, DashboardSerializer
)


class UserCourseEnrollmentViewSet(viewsets.ModelViewSet):
    """
    API viewset for course enrollments.
    
    GET /api/v1/enrollments/ - List user's enrollments
    POST /api/v1/enrollments/ - Enroll in a course
    GET /api/v1/enrollments/{id}/ - Get enrollment detail
    DELETE /api/v1/enrollments/{id}/ - Unenroll from course
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCourseEnrollmentCreateSerializer
        return UserCourseEnrollmentSerializer
    
    def get_queryset(self):
        return UserCourseEnrollment.objects.filter(
            user=self.request.user
        ).select_related('course', 'current_unit', 'current_lesson')
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update enrollment progress."""
        enrollment = self.get_object()
        enrollment.update_progress()
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active enrollments."""
        queryset = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserLessonProgressViewSet(viewsets.ModelViewSet):
    """
    API viewset for lesson progress.
    
    GET /api/v1/progress/lessons/ - List lesson progress
    GET /api/v1/progress/lessons/{lesson_id}/ - Get progress for specific lesson
    """
    
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'lesson_id'
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserLessonProgressUpdateSerializer
        return UserLessonProgressSerializer
    
    def get_queryset(self):
        return UserLessonProgress.objects.filter(
            user=self.request.user
        ).select_related('lesson', 'lesson__unit')
    
    def get_object(self):
        lesson_id = self.kwargs['lesson_id']
        progress, _ = UserLessonProgress.objects.get_or_create(
            user=self.request.user,
            lesson_id=lesson_id
        )
        return progress
    
    @action(detail=True, methods=['post'])
    def start(self, request, lesson_id=None):
        """Mark lesson as started."""
        progress = self.get_object()
        if progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.started_at = timezone.now()
            progress.save()
        serializer = self.get_serializer(progress)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, lesson_id=None):
        """Mark lesson as completed."""
        progress = self.get_object()
        score = request.data.get('score')
        time_spent = request.data.get('time_spent', 0)
        
        progress.mark_completed(score=score)
        progress.total_time_seconds += time_spent
        
        # Award XP
        if progress.lesson:
            xp = progress.lesson.xp_reward
            progress.xp_earned += xp
            progress.save()
            
            # Update user XP
            request.user.xp_points += xp
            request.user.save(update_fields=['xp_points'])
        
        serializer = self.get_serializer(progress)
        return Response(serializer.data)


class FlashcardSRSViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for SRS flashcard review.
    
    GET /api/v1/srs/flashcards/ - List user's flashcard progress
    GET /api/v1/srs/flashcards/due/ - Get flashcards due for review
    POST /api/v1/srs/flashcards/review/ - Submit review result
    """
    
    serializer_class = UserFlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFlashcard.objects.filter(
            user=self.request.user
        ).select_related('flashcard')
    
    @action(detail=False, methods=['get'])
    def due(self, request):
        """Get flashcards due for review."""
        limit = min(int(request.query_params.get('limit', 20)), 100)
        
        # Get due flashcards
        due_cards = self.get_queryset().filter(
            next_review_date__lte=timezone.now()
        ).order_by('next_review_date')[:limit]
        
        serializer = self.get_serializer(due_cards, many=True)
        return Response({
            'count': due_cards.count(),
            'flashcards': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def new(self, request):
        """Get new flashcards not yet studied."""
        limit = min(int(request.query_params.get('limit', 10)), 50)
        lesson_id = request.query_params.get('lesson')
        
        # Get flashcard IDs user has studied
        studied_ids = UserFlashcard.objects.filter(
            user=request.user
        ).values_list('flashcard_id', flat=True)
        
        # Get new flashcards
        queryset = Flashcard.objects.filter(is_active=True).exclude(id__in=studied_ids)
        
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        
        from apps.curriculum.serializers import FlashcardSerializer
        serializer = FlashcardSerializer(queryset[:limit], many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def review(self, request):
        """Submit flashcard review result."""
        serializer = FlashcardReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        flashcard_id = serializer.validated_data['flashcard_id']
        quality = serializer.validated_data['quality']
        
        # Get or create user flashcard
        user_flashcard, created = UserFlashcard.objects.get_or_create(
            user=request.user,
            flashcard_id=flashcard_id
        )
        
        # Process review
        user_flashcard.process_review(quality)
        
        result_serializer = UserFlashcardSerializer(user_flashcard)
        return Response(result_serializer.data)
    
    @action(detail=False, methods=['post'])
    def review_batch(self, request):
        """Submit batch flashcard reviews."""
        serializer = FlashcardReviewBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        results = []
        for review in serializer.validated_data['reviews']:
            user_flashcard, _ = UserFlashcard.objects.get_or_create(
                user=request.user,
                flashcard_id=review['flashcard_id']
            )
            user_flashcard.process_review(review['quality'])
            results.append(UserFlashcardSerializer(user_flashcard).data)
        
        return Response({
            'reviewed': len(results),
            'results': results
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get SRS statistics."""
        queryset = self.get_queryset()
        
        total = queryset.count()
        mastered = queryset.filter(is_mastered=True).count()
        learning = queryset.filter(is_mastered=False, review_count__gt=0).count()
        due_today = queryset.filter(next_review_date__lte=timezone.now()).count()
        
        # By box level
        by_box = queryset.values('box_level').annotate(count=Count('id'))
        box_distribution = {item['box_level']: item['count'] for item in by_box}
        
        return Response({
            'total': total,
            'mastered': mastered,
            'learning': learning,
            'due_today': due_today,
            'box_distribution': box_distribution,
            'mastery_rate': (mastered / total * 100) if total > 0 else 0
        })


class PracticeSessionViewSet(viewsets.ModelViewSet):
    """
    API viewset for practice sessions.
    
    GET /api/v1/practice/sessions/ - List practice sessions
    POST /api/v1/practice/sessions/ - Start new session
    PATCH /api/v1/practice/sessions/{id}/ - Update/complete session
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PracticeSessionCreateSerializer
        if self.action in ['update', 'partial_update']:
            return PracticeSessionUpdateSerializer
        return PracticeSessionSerializer
    
    def get_queryset(self):
        return PracticeSession.objects.filter(
            user=self.request.user
        ).select_related('lesson').prefetch_related('results')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a practice session."""
        session = self.get_object()
        
        if session.completed_at:
            return Response(
                {'error': 'Session đã hoàn thành.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.completed_at = timezone.now()
        session.duration_seconds = (
            session.completed_at - session.started_at
        ).total_seconds()
        
        # Calculate score
        if session.total_items > 0:
            session.score = Decimal(
                session.correct_items * 100 / session.total_items
            ).quantize(Decimal('0.01'))
        
        # Calculate XP
        base_xp = 10
        accuracy_bonus = int(float(session.score) / 10)
        session.xp_earned = base_xp + accuracy_bonus
        
        session.save()
        
        # Update user XP
        request.user.xp_points += session.xp_earned
        request.user.save(update_fields=['xp_points'])
        
        serializer = PracticeSessionSerializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_result(self, request, pk=None):
        """Add a result to the session."""
        session = self.get_object()
        
        serializer = PracticeResultCreateSerializer(data={
            **request.data,
            'session': session.id,
            'order': session.results.count() + 1
        })
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        # Update session counts
        session.total_items = F('total_items') + 1
        if result.result == 'correct':
            session.correct_items = F('correct_items') + 1
        elif result.result == 'incorrect':
            session.incorrect_items = F('incorrect_items') + 1
        elif result.result == 'skipped':
            session.skipped_items = F('skipped_items') + 1
        session.save()
        
        return Response(PracticeResultSerializer(result).data)


class DailyStreakViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for daily streaks.
    
    GET /api/v1/streaks/ - Get streak history
    GET /api/v1/streaks/calendar/ - Get calendar view
    """
    
    serializer_class = DailyStreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DailyStreak.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get calendar view of study days."""
        # Default to last 30 days
        days = min(int(request.query_params.get('days', 30)), 365)
        start_date = date.today() - timedelta(days=days)
        
        streaks = self.get_queryset().filter(
            study_date__gte=start_date
        ).order_by('study_date')
        
        serializer = self.get_serializer(streaks, many=True)
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': date.today().isoformat(),
            'days': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current streak info."""
        user = request.user
        
        return Response({
            'current_streak': user.streak_days,
            'longest_streak': user.longest_streak,
            'last_study_date': user.last_study_date,
            'studied_today': user.last_study_date == date.today()
        })


class LearningGoalViewSet(viewsets.ModelViewSet):
    """
    API viewset for learning goals.
    
    GET /api/v1/goals/ - List goals
    POST /api/v1/goals/ - Create goal
    PATCH /api/v1/goals/{id}/ - Update goal
    DELETE /api/v1/goals/{id}/ - Delete goal
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LearningGoalCreateSerializer
        return LearningGoalSerializer
    
    def get_queryset(self):
        return LearningGoal.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active goals."""
        queryset = self.get_queryset().filter(
            is_active=True,
            is_completed=False
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_progress(self, request, pk=None):
        """Check and update goal progress."""
        goal = self.get_object()
        completed = goal.check_completion()
        
        serializer = self.get_serializer(goal)
        return Response({
            'goal': serializer.data,
            'just_completed': completed
        })


class DashboardView(APIView):
    """
    API endpoint for dashboard data.
    
    GET /api/v1/dashboard/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Stats
        stats = {
            'total_xp': user.xp_points,
            'current_streak': user.streak_days,
            'longest_streak': user.longest_streak,
            'total_lessons_completed': UserLessonProgress.objects.filter(
                user=user, status='completed'
            ).count(),
            'total_flashcards_mastered': UserFlashcard.objects.filter(
                user=user, is_mastered=True
            ).count(),
            'total_study_time_minutes': UserLessonProgress.objects.filter(
                user=user
            ).aggregate(total=Sum('total_time_seconds'))['total'] or 0 // 60,
            'courses_enrolled': UserCourseEnrollment.objects.filter(
                user=user
            ).count(),
            'courses_completed': UserCourseEnrollment.objects.filter(
                user=user, status='completed'
            ).count(),
            'current_level': user.current_level,
            'achievements_unlocked': user.achievements.filter(
                is_unlocked=True
            ).count()
        }
        
        # Recent activity (last 5 sessions)
        recent_activity = PracticeSession.objects.filter(
            user=user
        ).order_by('-started_at')[:5]
        
        # Due flashcards count
        due_flashcards_count = UserFlashcard.objects.filter(
            user=user,
            next_review_date__lte=timezone.now()
        ).count()
        
        # Active goals
        active_goals = LearningGoal.objects.filter(
            user=user,
            is_active=True,
            is_completed=False
        )
        
        # Streak calendar (last 7 days)
        streak_calendar = DailyStreak.objects.filter(
            user=user,
            study_date__gte=date.today() - timedelta(days=7)
        ).order_by('study_date')
        
        # Current courses
        current_courses = UserCourseEnrollment.objects.filter(
            user=user,
            status='active'
        ).select_related('course')[:3]
        
        return Response({
            'stats': stats,
            'recent_activity': PracticeSessionSerializer(recent_activity, many=True).data,
            'due_flashcards_count': due_flashcards_count,
            'active_goals': LearningGoalSerializer(active_goals, many=True).data,
            'streak_calendar': DailyStreakSerializer(streak_calendar, many=True).data,
            'current_courses': UserCourseEnrollmentSerializer(current_courses, many=True).data
        })


class StudyStatsView(APIView):
    """
    API endpoint for detailed study statistics.
    
    GET /api/v1/stats/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        period = request.query_params.get('period', 'week')  # week, month, all
        
        # Calculate date range
        if period == 'week':
            start_date = date.today() - timedelta(days=7)
        elif period == 'month':
            start_date = date.today() - timedelta(days=30)
        else:
            start_date = None
        
        # Base querysets
        sessions_qs = PracticeSession.objects.filter(user=user)
        streaks_qs = DailyStreak.objects.filter(user=user)
        
        if start_date:
            sessions_qs = sessions_qs.filter(started_at__date__gte=start_date)
            streaks_qs = streaks_qs.filter(study_date__gte=start_date)
        
        # Aggregate stats
        session_stats = sessions_qs.aggregate(
            total_sessions=Count('id'),
            total_time=Sum('duration_seconds'),
            avg_score=Avg('score'),
            total_xp=Sum('xp_earned')
        )
        
        streak_stats = streaks_qs.aggregate(
            study_days=Count('id'),
            total_minutes=Sum('minutes_studied'),
            total_lessons=Sum('lessons_completed'),
            total_flashcards=Sum('flashcards_reviewed')
        )
        
        # By session type
        by_type = sessions_qs.values('session_type').annotate(
            count=Count('id'),
            avg_score=Avg('score')
        )
        
        return Response({
            'period': period,
            'sessions': {
                'total': session_stats['total_sessions'] or 0,
                'total_time_minutes': (session_stats['total_time'] or 0) // 60,
                'average_score': float(session_stats['avg_score'] or 0),
                'total_xp': session_stats['total_xp'] or 0
            },
            'activity': {
                'study_days': streak_stats['study_days'] or 0,
                'total_minutes': streak_stats['total_minutes'] or 0,
                'lessons_completed': streak_stats['total_lessons'] or 0,
                'flashcards_reviewed': streak_stats['total_flashcards'] or 0
            },
            'by_type': list(by_type)
        })
