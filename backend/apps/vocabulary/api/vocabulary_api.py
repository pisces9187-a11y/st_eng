"""
Vocabulary API Views

REST API endpoints for:
- Words (Oxford 3000/5000)
- Flashcard decks
- Study sessions
- Spaced repetition progress
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, Max
from datetime import timedelta

from ..models import Word, FlashcardDeck, Flashcard, UserFlashcardProgress, StudySession
from ..serializers import (
    WordSerializer, WordDetailSerializer,
    FlashcardDeckListSerializer, FlashcardDeckDetailSerializer,
    FlashcardSerializer, UserFlashcardProgressSerializer,
    ReviewFlashcardSerializer, StudySessionSerializer,
    StudyStatsSerializer
)


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for Oxford words
    
    List: GET /api/vocabulary/words/
    Detail: GET /api/vocabulary/words/{id}/
    Filter by level: GET /api/vocabulary/words/?level=A1
    Search: GET /api/vocabulary/words/?search=hello
    """
    
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WordDetailSerializer
        return WordSerializer
    
    def get_queryset(self):
        queryset = Word.objects.all()
        
        # Filter by CEFR level
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(cefr_level=level)
        
        # Filter by part of speech
        pos = self.request.query_params.get('pos')
        if pos:
            queryset = queryset.filter(pos__icontains=pos)
        
        # Search by text or meaning
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(text__icontains=search) |
                Q(meaning_vi__icontains=search) |
                Q(meaning_en__icontains=search)
            )
        
        return queryset


class FlashcardDeckViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for flashcard decks
    
    List: GET /api/vocabulary/decks/
    Detail: GET /api/vocabulary/decks/{id}/
    Study: GET /api/vocabulary/decks/{id}/study/ (get due cards)
    """
    
    queryset = FlashcardDeck.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FlashcardDeckDetailSerializer
        return FlashcardDeckListSerializer
    
    def get_queryset(self):
        """Only show public decks or user's own decks"""
        user = self.request.user
        return FlashcardDeck.objects.filter(
            Q(is_public=True) | Q(created_by=user)
        )
    
    @action(detail=True, methods=['get'])
    def study(self, request, pk=None):
        """
        Get flashcards due for review in this deck
        
        Returns cards that need review based on SM-2 algorithm:
        - New cards (never seen)
        - Due cards (next_review_date <= now)
        - Limited to 20 cards per session
        """
        deck = self.get_object()
        user = request.user
        
        # Get all flashcards in deck
        all_cards = deck.flashcards.all()
        
        # Get user's progress for these cards
        progress_map = {
            p.flashcard_id: p 
            for p in UserFlashcardProgress.objects.filter(
                user=user,
                flashcard__deck=deck
            )
        }
        
        # Separate into new and due cards
        new_cards = []
        due_cards = []
        
        for card in all_cards:
            progress = progress_map.get(card.id)
            
            if not progress:
                # New card (never seen)
                new_cards.append(card)
            elif progress.is_due:
                # Due for review
                due_cards.append(card)
        
        # Limit to 20 cards: 5 new + 15 due (or whatever's available)
        study_cards = due_cards[:15] + new_cards[:5]
        study_cards = study_cards[:20]  # Hard limit
        
        serializer = FlashcardSerializer(study_cards, many=True)
        
        return Response({
            'deck': FlashcardDeckListSerializer(deck).data,
            'cards': serializer.data,
            'total_new': len(new_cards),
            'total_due': len(due_cards),
            'cards_in_session': len(study_cards),
        })


class FlashcardProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoints for user's flashcard progress
    
    List user's progress: GET /api/vocabulary/progress/
    Review a card: POST /api/vocabulary/progress/{id}/review/
        Body: {"quality": 4}  (0-5 rating)
    """
    
    serializer_class = UserFlashcardProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show current user's progress"""
        return UserFlashcardProgress.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Submit a review for a flashcard
        
        Body: {
            "quality": 4  (0-5: 0=blackout, 3=correct with effort, 5=perfect)
        }
        
        This updates the SM-2 algorithm and schedules next review.
        """
        progress = self.get_object()
        serializer = ReviewFlashcardSerializer(data=request.data)
        
        if serializer.is_valid():
            quality = serializer.validated_data['quality']
            
            # Calculate next review using SM-2 algorithm
            progress.calculate_next_review(quality)
            
            # Return updated progress
            return Response(
                UserFlashcardProgressSerializer(progress).data
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudySessionViewSet(viewsets.ModelViewSet):
    """
    API endpoints for study sessions
    
    Start session: POST /api/vocabulary/sessions/
        Body: {"deck": 1}
    
    End session: POST /api/vocabulary/sessions/{id}/end/
        Body: {
            "cards_studied": 15,
            "cards_correct": 12,
            "cards_incorrect": 3
        }
    
    List sessions: GET /api/vocabulary/sessions/
    """
    
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show current user's sessions"""
        return StudySession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically set user when creating session"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """
        End a study session and calculate metrics
        
        Body: {
            "cards_studied": 15,
            "cards_correct": 12,
            "cards_incorrect": 3,
            "cards_skipped": 0,
            "notes": "Great session!"
        }
        """
        session = self.get_object()
        
        # Update session data
        session.cards_studied = request.data.get('cards_studied', 0)
        session.cards_correct = request.data.get('cards_correct', 0)
        session.cards_incorrect = request.data.get('cards_incorrect', 0)
        session.cards_skipped = request.data.get('cards_skipped', 0)
        session.notes = request.data.get('notes', '')
        
        # End session (calculates metrics)
        session.end_session()
        
        return Response(StudySessionSerializer(session).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get overall study statistics for current user
        
        Returns:
        - Total words learned
        - Words mastered
        - Total study time
        - Average accuracy
        - Current/best streak
        - Cards due today
        """
        user = request.user
        
        # Get progress stats
        progress_qs = UserFlashcardProgress.objects.filter(user=user)
        total_words = progress_qs.count()
        words_mastered = progress_qs.filter(is_mastered=True).count()
        words_learning = progress_qs.filter(is_learning=True).count()
        
        # Calculate streaks
        if total_words > 0:
            best_streak = progress_qs.aggregate(Max('best_streak'))['best_streak__max'] or 0
            current_streak = progress_qs.aggregate(Avg('streak'))['streak__avg'] or 0
        else:
            best_streak = 0
            current_streak = 0
        
        # Cards due today
        cards_due = progress_qs.filter(
            next_review_date__lte=timezone.now()
        ).count()
        
        # Session stats
        sessions = StudySession.objects.filter(user=user)
        total_sessions = sessions.count()
        total_study_time = sessions.aggregate(
            Sum('time_spent_seconds')
        )['time_spent_seconds__sum'] or 0
        
        avg_accuracy = sessions.filter(
            cards_studied__gt=0
        ).aggregate(Avg('accuracy'))['accuracy__avg'] or 0
        
        stats_data = {
            'total_words_learned': total_words,
            'words_mastered': words_mastered,
            'words_learning': words_learning,
            'total_study_time_minutes': int(total_study_time / 60),
            'total_sessions': total_sessions,
            'average_accuracy': round(avg_accuracy, 1),
            'current_streak': int(current_streak),
            'best_streak': best_streak,
            'cards_due_today': cards_due,
        }
        
        serializer = StudyStatsSerializer(stats_data)
        return Response(serializer.data)

