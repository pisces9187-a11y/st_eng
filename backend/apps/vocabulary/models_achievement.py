"""
Achievement System Models

Gamification features to increase user engagement and motivation.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Achievement(models.Model):
    """
    Achievement definitions.
    
    Examples:
    - First Steps: Learn your first 10 cards
    - Week Warrior: Maintain a 7-day streak
    - Speed Demon: Learn 50 cards in one day
    """
    
    CATEGORY_CHOICES = [
        ('milestone', 'Milestone'),     # Cards learned milestones
        ('streak', 'Streak'),           # Consecutive days
        ('speed', 'Speed'),             # Cards per day
        ('mastery', 'Mastery'),         # Accuracy achievements
        ('level', 'Level'),             # Level completion
    ]
    
    # Unique identifier
    key = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique key: first_10_cards, streak_7_days, etc."
    )
    
    # Display information
    name = models.CharField(max_length=200, help_text="Display name: 🎓 First Steps")
    description = models.TextField(help_text="Description: Learned your first 10 cards")
    icon = models.CharField(max_length=50, help_text="Emoji or icon class: 🎓 or fas fa-trophy")
    
    # Category
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Requirements
    requirement_type = models.CharField(
        max_length=50,
        help_text="Type: cards_learned, streak_days, accuracy_rate, level_completed"
    )
    requirement_value = models.IntegerField(
        help_text="Required value to unlock"
    )
    
    # Additional criteria (JSON)
    requirement_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional criteria: {'level': 'A1', 'timeframe': 'day'}"
    )
    
    # Rewards
    points = models.IntegerField(default=10, help_text="Points awarded")
    
    # Order
    order = models.IntegerField(default=0, help_text="Display order")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'order', 'requirement_value']
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
    
    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def check_user_qualifies(self, user):
        """
        Check if user qualifies for this achievement.
        
        Returns:
            bool: True if user meets requirements
        """
        from .models import UserFlashcardProgress, StudySession
        
        if self.requirement_type == 'cards_learned':
            # Count total cards learned
            total = UserFlashcardProgress.objects.filter(
                user=user,
                total_reviews__gt=0
            ).count()
            return total >= self.requirement_value
        
        elif self.requirement_type == 'streak_days':
            # Check current streak (streak_days is on User model)
            current_streak = getattr(user, 'streak_days', 0)
            return current_streak >= self.requirement_value
        
        elif self.requirement_type == 'cards_per_day':
            # Count cards learned today
            today = timezone.now().date()
            today_count = UserFlashcardProgress.objects.filter(
                user=user,
                last_reviewed_at__date=today
            ).count()
            return today_count >= self.requirement_value
        
        elif self.requirement_type == 'accuracy_rate':
            # Calculate overall accuracy
            progress = UserFlashcardProgress.objects.filter(user=user)
            if not progress.exists():
                return False
            
            total_reviews = sum(p.total_reviews for p in progress)
            total_correct = sum(p.total_correct for p in progress)
            
            if total_reviews == 0:
                return False
            
            accuracy = (total_correct / total_reviews) * 100
            return accuracy >= self.requirement_value
        
        elif self.requirement_type == 'level_completed':
            # Check if level is mastered (80% of words)
            level = self.requirement_data.get('level') if self.requirement_data else None
            if not level:
                return False
            
            from .models import Word
            total_words = Word.objects.filter(cefr_level=level).count()
            mastered_words = UserFlashcardProgress.objects.filter(
                user=user,
                flashcard__word__cefr_level=level,
                is_mastered=True
            ).count()
            
            if total_words == 0:
                return False
            
            completion_rate = (mastered_words / total_words) * 100
            return completion_rate >= 80
        
        return False


class UserAchievement(models.Model):
    """
    User's unlocked achievements.
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='unlocked_achievements'
    )
    achievement = models.ForeignKey(
        Achievement, 
        on_delete=models.CASCADE,
        related_name='unlocked_by_users'
    )
    
    # Unlock data
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    # Notification status
    is_notified = models.BooleanField(
        default=False,
        help_text="Has user been notified about this achievement?"
    )
    
    class Meta:
        unique_together = [['user', 'achievement']]
        ordering = ['-unlocked_at']
        verbose_name = "User Achievement"
        verbose_name_plural = "User Achievements"
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


def check_and_unlock_achievements(user):
    """
    Check all achievements and unlock any that user qualifies for.
    
    Args:
        user: User instance
    
    Returns:
        list: List of newly unlocked achievements
    """
    newly_unlocked = []
    
    # Get all active achievements
    all_achievements = Achievement.objects.filter(is_active=True)
    
    # Get already unlocked achievement IDs
    unlocked_ids = UserAchievement.objects.filter(
        user=user
    ).values_list('achievement_id', flat=True)
    
    # Check each achievement
    for achievement in all_achievements:
        # Skip if already unlocked
        if achievement.id in unlocked_ids:
            continue
        
        # Check if user qualifies
        if achievement.check_user_qualifies(user):
            # Unlock achievement
            user_achievement = UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )
            newly_unlocked.append(achievement)
    
    return newly_unlocked
