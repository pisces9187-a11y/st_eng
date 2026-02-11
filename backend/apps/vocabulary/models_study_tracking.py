"""
Models for tracking user's flashcard study progress and history.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class DeckStudyHistory(models.Model):
    """
    Track user's study history and aggregated stats per deck.
    Updated after each study session completion.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='deck_histories'
    )
    deck = models.ForeignKey(
        'FlashcardDeck',
        on_delete=models.CASCADE,
        related_name='study_histories'
    )
    
    # Aggregated session stats
    total_sessions = models.IntegerField(
        default=0,
        help_text="Total number of study sessions completed"
    )
    total_cards_studied = models.IntegerField(
        default=0,
        help_text="Total cards studied across all sessions"
    )
    total_time_minutes = models.IntegerField(
        default=0,
        help_text="Total study time in minutes"
    )
    
    # Progress tracking (cached for performance)
    cards_new = models.IntegerField(
        default=0,
        help_text="Number of cards not yet studied"
    )
    cards_learning = models.IntegerField(
        default=0,
        help_text="Number of cards currently being learned"
    )
    cards_mastered = models.IntegerField(
        default=0,
        help_text="Number of cards mastered (SM-2 mastered)"
    )
    cards_difficult = models.IntegerField(
        default=0,
        help_text="Number of cards marked as difficult (low easiness_factor)"
    )
    progress_percentage = models.FloatField(
        default=0.0,
        help_text="Overall progress percentage (0-100)"
    )
    
    # Timestamps
    first_studied_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user first started studying this deck"
    )
    last_studied_at = models.DateTimeField(
        auto_now=True,
        help_text="When user last studied this deck"
    )
    last_progress_update = models.DateTimeField(
        default=timezone.now,
        help_text="When progress stats were last calculated"
    )
    
    class Meta:
        verbose_name = "Deck Study History"
        verbose_name_plural = "Deck Study Histories"
        unique_together = ['user', 'deck']
        ordering = ['-last_studied_at']
        indexes = [
            models.Index(fields=['user', '-last_studied_at']),
            models.Index(fields=['user', 'deck']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.deck.name} ({self.progress_percentage}%)"
    
    def update_progress(self):
        """Recalculate progress stats from UserFlashcardProgress"""
        from .models import UserFlashcardProgress
        
        total_cards = self.deck.flashcards.count()
        if total_cards == 0:
            return
        
        # Get user's progress for this deck
        progress_qs = UserFlashcardProgress.objects.filter(
            user=self.user,
            flashcard__deck=self.deck
        )
        
        self.cards_mastered = progress_qs.filter(is_mastered=True).count()
        self.cards_learning = progress_qs.filter(
            is_learning=True,
            is_mastered=False
        ).count()
        self.cards_difficult = progress_qs.filter(
            easiness_factor__lt=2.5
        ).count()
        
        cards_learned = progress_qs.count()
        self.cards_new = total_cards - cards_learned
        self.progress_percentage = round((cards_learned / total_cards * 100), 1)
        self.last_progress_update = timezone.now()
        self.save()


class UserCardTag(models.Model):
    """
    Allow users to tag flashcards for custom organization and review.
    Users can mark cards as difficult, important, or for later review.
    """
    TAG_CHOICES = [
        ('difficult', '🔴 Difficult'),
        ('review_later', '📝 Review Later'),
        ('important', '⭐ Important'),
        ('mastered', '✅ Mastered'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='card_tags'
    )
    flashcard = models.ForeignKey(
        'Flashcard',
        on_delete=models.CASCADE,
        related_name='user_tags'
    )
    tag = models.CharField(
        max_length=20,
        choices=TAG_CHOICES,
        help_text="Type of tag applied to the card"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the tag was added"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes about why this card was tagged"
    )
    
    class Meta:
        verbose_name = "User Card Tag"
        verbose_name_plural = "User Card Tags"
        unique_together = ['user', 'flashcard', 'tag']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'tag']),
            models.Index(fields=['flashcard', 'tag']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.flashcard.word.text} [{self.get_tag_display()}]"
