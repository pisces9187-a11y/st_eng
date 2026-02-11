"""
API Views for Flashcard Study System.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Sum

from .models import Flashcard, FlashcardDeck, UserFlashcardProgress, StudySession
from .models_achievement import Achievement, check_and_unlock_achievements
from .serializers_flashcard import (
    FlashcardStudySerializer, FlashcardDeckSerializer,
    StudySessionSerializer, ReviewCardRequestSerializer,
    AchievementSerializer, DailyProgressSerializer, StreakSerializer
)
from .utils_flashcard import (
    get_cards_for_study, calculate_daily_progress, update_user_streak
)


class FlashcardStudyViewSet(viewsets.ViewSet):
    """
    ViewSet for flashcard study sessions.
    
    Endpoints:
    - POST /study/session/start/ - Start new study session
    - POST /study/card/{id}/review/ - Review a card
    - GET /study/due/ - Get cards due for review
    - POST /study/session/{id}/end/ - End study session
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """
        Start a new study session with optional review mode.
        
        Request body:
        {
            "deck_id": 1,              // Optional
            "level": "A1",             // Optional
            "card_count": 20,          // Optional, default: 20
            "review_mode": "normal"    // Optional: normal, difficult, due, failed, tagged
            "tag": "difficult"         // Required if review_mode=tagged
        }
        """
        from .utils_flashcard import (
            get_cards_for_study, get_difficult_cards,
            get_due_cards, get_failed_cards, get_tagged_cards
        )
        
        # Get parameters
        deck_id = request.data.get('deck_id')
        level = request.data.get('level', request.user.current_level)
        card_count = request.data.get('card_count', 20)
        review_mode = request.data.get('review_mode', 'normal')
        tag = request.data.get('tag')
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[START_SESSION] Request data: {request.data}")
        logger.info(f"[START_SESSION] deck_id={deck_id}, level={level}, card_count={card_count}, mode={review_mode}")
        
        # Validate card_count
        if card_count < 1 or card_count > 100:
            return Response(
                {'error': 'card_count must be between 1 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get deck
        if deck_id:
            try:
                deck = FlashcardDeck.objects.get(id=deck_id)
            except FlashcardDeck.DoesNotExist:
                return Response(
                    {'error': 'Deck not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Get default deck for level
            deck = FlashcardDeck.objects.filter(
                level=level,
                is_official=True
            ).first()
            
            if not deck:
                return Response(
                    {'error': f'No official deck found for level {level}'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get cards based on review mode
        if review_mode == 'difficult':
            cards = get_difficult_cards(request.user, deck.id, card_count)
        elif review_mode == 'due':
            cards = get_due_cards(request.user, deck.id, card_count)
        elif review_mode == 'failed':
            cards = get_failed_cards(request.user, deck.id, card_count)
        elif review_mode == 'tagged':
            if not tag:
                return Response(
                    {'error': 'tag parameter required for review_mode=tagged'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cards = get_tagged_cards(request.user, tag, deck.id, card_count)
        else:  # normal mode
            cards = get_cards_for_study(
                user=request.user,
                level=level,
                limit=card_count,
                deck_id=deck_id  # Pass deck_id for filtering
            )
        
        logger.info(f"[START_SESSION] Review mode '{review_mode}' returned {len(cards)} cards")
        
        if not cards:
            return Response({
                'message': 'No cards available for study',
                'cards': []
            })
        
        # Create study session
        session = StudySession.objects.create(
            user=request.user,
            deck=deck,
            streak_count=request.user.streak_days,
            daily_goal=20  # TODO: Get from user profile
        )
        
        # Get daily progress
        daily_progress = calculate_daily_progress(request.user)
        
        # Serialize cards
        serializer = FlashcardStudySerializer(
            cards,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'session_id': session.id,
            'cards': serializer.data,
            'daily_progress': daily_progress,
            'streak': {
                'current': request.user.streak_days,
                'longest': request.user.longest_streak
            }
        })
    
    @action(detail=True, methods=['post'], url_path='review')
    def review_card(self, request, pk=None):
        """
        Review a flashcard and update progress.
        
        URL: /study/card/{card_id}/review/
        
        Request body:
        {
            "quality": 4,           // 0-5 (SM-2 quality rating)
            "time_spent": 8         // seconds (optional)
        }
        """
        # Validate request data
        serializer = ReviewCardRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quality = serializer.validated_data['quality']
        time_spent = serializer.validated_data.get('time_spent', 0)
        
        # Get flashcard
        try:
            flashcard = Flashcard.objects.get(id=pk)
        except Flashcard.DoesNotExist:
            return Response(
                {'error': 'Flashcard not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create progress
        progress, created = UserFlashcardProgress.objects.get_or_create(
            user=request.user,
            flashcard=flashcard,
            defaults={'next_review_date': timezone.now()}
        )
        
        # Apply SM-2 algorithm
        progress.calculate_next_review(quality)
        
        # Update streak
        streak_info = update_user_streak(request.user)
        
        # Get daily progress
        daily_progress = calculate_daily_progress(request.user)
        
        # Check for achievements
        newly_unlocked = check_and_unlock_achievements(request.user)
        achievement_data = AchievementSerializer(
            newly_unlocked,
            many=True,
            context={'request': request}
        ).data if newly_unlocked else []
        
        return Response({
            'next_review_date': progress.next_review_date,
            'interval': progress.interval,
            'easiness_factor': progress.easiness_factor,
            'is_mastered': progress.is_mastered,
            'total_reviews': progress.total_reviews,
            'accuracy': progress.accuracy,
            'streak': streak_info,
            'daily_progress': daily_progress,
            'achievements_unlocked': achievement_data
        })
    
    @action(detail=False, methods=['get'])
    def due(self, request):
        """
        Get cards due for review.
        
        Query params:
        - level: Filter by CEFR level
        - limit: Number of cards (default: 20)
        """
        level = request.query_params.get('level')
        limit = int(request.query_params.get('limit', 20))
        
        # Get due cards
        due_progress = UserFlashcardProgress.objects.filter(
            user=request.user,
            next_review_date__lte=timezone.now(),
            is_learning=True
        ).select_related('flashcard__word')
        
        if level:
            due_progress = due_progress.filter(
                flashcard__word__cefr_level=level
            )
        
        # Get flashcards
        due_cards = [p.flashcard for p in due_progress[:limit]]
        
        # Count by level
        by_level = {}
        for lvl in ['A1', 'A2', 'B1', 'B2', 'C1']:
            count = due_progress.filter(
                flashcard__word__cefr_level=lvl
            ).count()
            if count > 0:
                by_level[lvl] = count
        
        # Serialize
        serializer = FlashcardStudySerializer(
            due_cards,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'cards': serializer.data,
            'total_due': due_progress.count(),
            'by_level': by_level
        })
    
    @action(detail=True, methods=['post'], url_path='end')
    def end_session(self, request, pk=None):
        """
        End a study session and calculate stats.
        
        URL: /study/session/{session_id}/end/
        
        Request body:
        {
            "cards_studied": 20,
            "cards_correct": 17,
            "time_spent": 900       // seconds
        }
        """
        # Get session
        try:
            session = StudySession.objects.get(id=pk, user=request.user)
        except StudySession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update session
        session.ended_at = timezone.now()
        session.cards_studied = request.data.get('cards_studied', 0)
        session.cards_correct = request.data.get('cards_correct', 0)
        session.cards_incorrect = session.cards_studied - session.cards_correct
        session.time_spent_seconds = request.data.get('time_spent', 0)
        
        # Calculate metrics
        if session.cards_studied > 0:
            session.accuracy = round(
                (session.cards_correct / session.cards_studied) * 100,
                1
            )
            session.average_time_per_card = round(
                session.time_spent_seconds / session.cards_studied,
                1
            )
        
        # Save session first before calculating daily progress
        session.save()
        
        # Update daily goal progress (after save so this session is included)
        daily_progress = calculate_daily_progress(request.user)
        session.cards_goal_today = daily_progress['cards_today']
        session.is_goal_reached = daily_progress['is_goal_reached']
        session.save()
        
        # Update DeckStudyHistory
        deck_history = None
        if session.deck:
            from .models_study_tracking import DeckStudyHistory
            
            deck_history, created = DeckStudyHistory.objects.get_or_create(
                user=request.user,
                deck=session.deck
            )
            
            # Update aggregated stats
            deck_history.total_sessions += 1
            deck_history.total_cards_studied += session.cards_studied
            deck_history.total_time_minutes += session.duration_minutes
            deck_history.save()
            
            # Recalculate progress
            deck_history.update_progress()
        
        # Get deck progress if session has deck
        deck_progress = None
        if session.deck:
            total_cards = session.deck.flashcards.count()
            user_progress = UserFlashcardProgress.objects.filter(
                user=request.user,
                flashcard__deck=session.deck
            )
            
            learned_count = user_progress.count()
            mastered_count = user_progress.filter(is_mastered=True).count()
            learning_count = user_progress.filter(is_learning=True, is_mastered=False).count()
            
            deck_progress = {
                'deck_name': session.deck.name,
                'deck_level': session.deck.level,
                'total_cards': total_cards,
                'cards_learned': learned_count,
                'cards_mastered': mastered_count,
                'cards_learning': learning_count,
                'cards_new': total_cards - learned_count,
                'progress_percentage': round((learned_count / total_cards * 100), 1) if total_cards > 0 else 0
            }
        
        # Check achievements
        newly_unlocked = check_and_unlock_achievements(request.user)
        achievement_data = AchievementSerializer(
            newly_unlocked,
            many=True,
            context={'request': request}
        ).data if newly_unlocked else []
        
        # Serialize session
        session_serializer = StudySessionSerializer(session)
        
        return Response({
            'session': session_serializer.data,
            'session_stats': {
                'cards_studied': session.cards_studied,
                'accuracy': session.accuracy,
                'time_spent': f"{session.duration_minutes} minutes",
                'avg_time_per_card': f"{session.average_time_per_card}s"
            },
            'deck_progress': deck_progress,
            'achievements_unlocked': achievement_data,
            'streak_updated': True,
            'new_streak': request.user.streak_days,
            'goal_reached': session.is_goal_reached
        })


class FlashcardDeckViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for flashcard decks.
    
    Endpoints:
    - GET /decks/ - List all decks
    - GET /decks/{id}/ - Get deck details
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = FlashcardDeckSerializer
    
    def get_queryset(self):
        """Get decks - public decks or user's own decks."""
        return FlashcardDeck.objects.filter(
            is_public=True
        ).annotate(
            card_count=Count('flashcards')
        ).order_by('level', 'name')
    
    def list(self, request):
        """List all available decks with progress."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'decks': serializer.data
        })


class ProgressDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for progress and statistics.
    
    Endpoints:
    - GET /progress/dashboard/ - Get dashboard statistics
    - GET /progress/achievements/ - Get achievements
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive dashboard statistics."""
        user = request.user
        today = timezone.now().date()
        
        # Today's progress
        today_progress = calculate_daily_progress(user)
        
        # Week's progress
        week_start = today - timezone.timedelta(days=7)
        week_sessions = StudySession.objects.filter(
            user=user,
            started_at__gte=week_start
        )
        
        week_stats = week_sessions.aggregate(
            cards=Sum('cards_studied'),
            time=Sum('time_spent_seconds'),
            accuracy=Avg('accuracy')
        )
        
        # Days active this week
        days_active = week_sessions.values('started_at__date').distinct().count()
        
        # Level progress
        levels_progress = {}
        for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
            from .models import Word
            total = Word.objects.filter(cefr_level=level).count()
            learned = UserFlashcardProgress.objects.filter(
                user=user,
                flashcard__word__cefr_level=level,
                total_reviews__gt=0
            ).count()
            mastered = UserFlashcardProgress.objects.filter(
                user=user,
                flashcard__word__cefr_level=level,
                is_mastered=True
            ).count()
            
            levels_progress[level] = {
                'learned': learned,
                'total': total,
                'mastered': mastered,
                'percentage': int((learned / total) * 100) if total > 0 else 0
            }
        
        # Upcoming reviews
        upcoming = UserFlashcardProgress.objects.filter(
            user=user,
            next_review_date__lte=timezone.now() + timezone.timedelta(days=1),
            is_learning=True
        ).count()
        
        return Response({
            'today': {
                'cards_learned': today_progress['cards_learned'],
                'time_spent': today_progress['time_spent_minutes'],
                'goal_progress': today_progress['percentage']
            },
            'week': {
                'cards_learned': week_stats['cards'] or 0,
                'time_spent': int((week_stats['time'] or 0) / 60),
                'accuracy': round(week_stats['accuracy'] or 0, 1),
                'days_active': days_active
            },
            'streak': {
                'current': user.streak_days,
                'longest': user.longest_streak
            },
            'levels': levels_progress,
            'upcoming_reviews': upcoming
        })
    
    @action(detail=False, methods=['get'])
    def achievements(self, request):
        """Get user's achievements."""
        # Get all achievements
        all_achievements = Achievement.objects.filter(is_active=True)
        
        # Get unlocked achievements
        unlocked_ids = request.user.unlocked_achievements.values_list(
            'achievement_id',
            flat=True
        )
        
        unlocked = all_achievements.filter(id__in=unlocked_ids)
        locked = all_achievements.exclude(id__in=unlocked_ids)
        
        return Response({
            'unlocked': AchievementSerializer(
                unlocked,
                many=True,
                context={'request': request}
            ).data,
            'locked': AchievementSerializer(
                locked,
                many=True,
                context={'request': request}
            ).data,
            'total_unlocked': unlocked.count(),
            'total_points': sum(a.points for a in unlocked)
        })


class FlashcardDeckViewSet(viewsets.ViewSet):
    """
    ViewSet for managing flashcard decks and study history.
    
    New endpoints for progress tracking and review modes.
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get user's 5 most recently studied decks with progress.
        
        GET /api/v1/vocabulary/flashcards/decks/recent/
        
        Returns:
        [
            {
                "deck": {...},
                "last_studied_at": "2026-01-08T10:30:00Z",
                "total_sessions": 5,
                "progress_percentage": 67.5,
                "cards_mastered": 150,
                "cards_learning": 50,
                "cards_new": 100
            }
        ]
        """
        from .models_study_tracking import DeckStudyHistory
        
        # Get recent decks
        recent_histories = DeckStudyHistory.objects.filter(
            user=request.user
        ).select_related('deck').order_by('-last_studied_at')[:5]
        
        if not recent_histories:
            return Response([])
        
        # Build response
        results = []
        for history in recent_histories:
            results.append({
                'deck': {
                    'id': history.deck.id,
                    'name': history.deck.name,
                    'description': history.deck.description,
                    'level': history.deck.level,
                    'icon': history.deck.icon,
                    'color': history.deck.color,
                    'card_count': history.deck.flashcards.count()
                },
                'last_studied_at': history.last_studied_at,
                'total_sessions': history.total_sessions,
                'total_cards_studied': history.total_cards_studied,
                'total_time_minutes': history.total_time_minutes,
                'progress_percentage': history.progress_percentage,
                'cards_mastered': history.cards_mastered,
                'cards_learning': history.cards_learning,
                'cards_new': history.cards_new,
                'cards_difficult': history.cards_difficult
            })
        
        return Response(results)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """
        Get detailed progress for a specific deck.
        
        GET /api/v1/vocabulary/flashcards/decks/{deck_id}/progress/
        
        Returns detailed breakdown of user's progress in this deck.
        """
        from .models_study_tracking import DeckStudyHistory
        
        try:
            deck = FlashcardDeck.objects.get(pk=pk)
        except FlashcardDeck.DoesNotExist:
            return Response(
                {'error': 'Deck not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create history
        history, created = DeckStudyHistory.objects.get_or_create(
            user=request.user,
            deck=deck
        )
        
        # Update progress if needed
        if created or (timezone.now() - history.last_progress_update).total_seconds() > 300:
            history.update_progress()
        
        # Get user's progress entries
        progress_qs = UserFlashcardProgress.objects.filter(
            user=request.user,
            flashcard__deck=deck
        )
        
        # Calculate detailed stats
        total_cards = deck.flashcards.count()
        difficult_cards = progress_qs.filter(easiness_factor__lt=2.5).count()
        due_cards = progress_qs.filter(
            next_review_date__lte=timezone.now().date()
        ).count()
        
        return Response({
            'deck': FlashcardDeckSerializer(deck).data,
            'history': {
                'first_studied_at': history.first_studied_at,
                'last_studied_at': history.last_studied_at,
                'total_sessions': history.total_sessions,
                'total_cards_studied': history.total_cards_studied,
                'total_time_minutes': history.total_time_minutes
            },
            'progress': {
                'total_cards': total_cards,
                'cards_new': history.cards_new,
                'cards_learning': history.cards_learning,
                'cards_mastered': history.cards_mastered,
                'cards_difficult': difficult_cards,
                'cards_due': due_cards,
                'progress_percentage': history.progress_percentage
            }
        })
    
    @action(detail=True, methods=['post'], url_path='tag-card')
    def tag_card(self, request, pk=None):
        """
        Tag/untag a flashcard.
        
        POST /api/v1/vocabulary/flashcards/{card_id}/tag-card/
        
        Request body:
        {
            "tag": "difficult",     // difficult, review_later, important, mastered
            "action": "add",        // add or remove
            "notes": "..."          // optional
        }
        """
        from .models_study_tracking import UserCardTag
        
        try:
            flashcard = Flashcard.objects.get(pk=pk)
        except Flashcard.DoesNotExist:
            return Response(
                {'error': 'Flashcard not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        tag = request.data.get('tag')
        action = request.data.get('action', 'add')
        notes = request.data.get('notes', '')
        
        # Validate tag
        valid_tags = ['difficult', 'review_later', 'important', 'mastered']
        if tag not in valid_tags:
            return Response(
                {'error': f'Invalid tag. Must be one of: {", ".join(valid_tags)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'add':
            # Add tag (or update if exists)
            card_tag, created = UserCardTag.objects.get_or_create(
                user=request.user,
                flashcard=flashcard,
                tag=tag,
                defaults={'notes': notes}
            )
            
            if not created:
                card_tag.notes = notes
                card_tag.save()
            
            return Response({
                'message': 'Tag added',
                'tag': tag,
                'created': created
            })
        
        elif action == 'remove':
            # Remove tag
            deleted_count = UserCardTag.objects.filter(
                user=request.user,
                flashcard=flashcard,
                tag=tag
            ).delete()[0]
            
            return Response({
                'message': 'Tag removed' if deleted_count > 0 else 'Tag not found',
                'deleted': deleted_count > 0
            })
        
        else:
            return Response(
                {'error': 'Invalid action. Must be "add" or "remove"'},
                status=status.HTTP_400_BAD_REQUEST
            )
