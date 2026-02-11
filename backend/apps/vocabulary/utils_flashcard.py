"""
Utility functions for Flashcard system.
"""

from django.db import transaction
from .models import Word, Flashcard, FlashcardDeck


def create_flashcards_from_words():
    """
    Create flashcards from all words in database.
    Organized by CEFR level into separate decks.
    
    Returns:
        dict: Statistics about created flashcards
    """
    
    stats = {
        'decks_created': 0,
        'flashcards_created': 0,
        'flashcards_updated': 0,
        'by_level': {}
    }
    
    # CEFR levels
    levels = ['A1', 'A2', 'B1', 'B2', 'C1']
    
    for level in levels:
        # Get or create deck for this level
        deck, deck_created = FlashcardDeck.objects.get_or_create(
            name=f"Oxford {level}",
            defaults={
                'description': f'Oxford {level} essential vocabulary',
                'category': 'oxford',
                'level': level,
                'is_public': True,
                'is_official': True,
                'icon': '📚',
                'color': get_level_color(level),
                'created_by_id': 1  # Admin user
            }
        )
        
        if deck_created:
            stats['decks_created'] += 1
        
        # Get words for this level
        words = Word.objects.filter(cefr_level=level)
        
        level_created = 0
        level_updated = 0
        
        for word in words:
            # Create front text
            front_text = f"{word.text}"
            
            # Create back text with meaning and example
            back_text = f"{word.meaning_vi}"
            if word.example_en:
                back_text += f"\n\nExample: {word.example_en}"
            if word.example_vi:
                back_text += f"\n{word.example_vi}"
            
            # Get or create flashcard
            flashcard, created = Flashcard.objects.get_or_create(
                word=word,
                deck=deck,
                defaults={
                    'front_text': front_text,
                    'back_text': back_text,
                    'front_type': 'word',
                    'difficulty': calculate_difficulty(word),
                    'hint': f"Part of speech: {word.pos}",
                    'audio_url': '',  # Will be generated on demand
                    'order': 0
                }
            )
            
            if created:
                level_created += 1
            else:
                # Update existing flashcard
                flashcard.front_text = front_text
                flashcard.back_text = back_text
                flashcard.save()
                level_updated += 1
        
        stats['by_level'][level] = {
            'created': level_created,
            'updated': level_updated,
            'total': words.count()
        }
        
        stats['flashcards_created'] += level_created
        stats['flashcards_updated'] += level_updated
    
    return stats


def get_level_color(level):
    """Get color for CEFR level."""
    colors = {
        'A1': '#4ade80',  # Green
        'A2': '#facc15',  # Yellow
        'B1': '#fb923c',  # Orange
        'B2': '#ef4444',  # Red
        'C1': '#8b5cf6',  # Purple
        'C2': '#06b6d4',  # Cyan
    }
    return colors.get(level, '#F47C26')


def calculate_difficulty(word):
    """
    Calculate difficulty score for a word (1-5).
    Based on CEFR level and word length.
    
    Args:
        word: Word instance
    
    Returns:
        int: Difficulty score (1=easy, 5=hard)
    """
    # Base difficulty by CEFR level
    level_difficulty = {
        'A1': 1,
        'A2': 2,
        'B1': 3,
        'B2': 4,
        'C1': 5,
        'C2': 5
    }
    
    difficulty = level_difficulty.get(word.cefr_level, 3)
    
    # Adjust for word length
    if len(word.text) > 12:
        difficulty = min(5, difficulty + 1)
    
    # Adjust for multiple meanings or complex POS
    if word.pos in ['phrasal verb', 'idiom']:
        difficulty = min(5, difficulty + 1)
    
    return difficulty


def get_cards_for_study(user, level=None, limit=20, deck_id=None):
    """
    Smart card selection algorithm for study session.
    
    Priority:
    1. Cards due for review (70%)
    2. New cards (30%)
    
    Args:
        user: User instance
        level: CEFR level filter (optional)
        limit: Number of cards to return
        deck_id: Specific deck to study from (optional)
    
    Returns:
        list: List of Flashcard instances
    """
    from .models import UserFlashcardProgress
    from django.utils import timezone
    import random
    
    # Get cards due for review
    due_progress = UserFlashcardProgress.objects.filter(
        user=user,
        next_review_date__lte=timezone.now(),
        is_learning=True
    ).select_related('flashcard__word')
    
    if level:
        due_progress = due_progress.filter(flashcard__word__cefr_level=level)
    
    if deck_id:
        due_progress = due_progress.filter(flashcard__deck_id=deck_id)
    
    # Get new cards (not yet studied)
    studied_card_ids = UserFlashcardProgress.objects.filter(
        user=user
    ).values_list('flashcard_id', flat=True)
    
    new_cards = Flashcard.objects.exclude(
        id__in=studied_card_ids
    ).select_related('word', 'deck')
    
    # Filter by deck if specified
    if deck_id:
        new_cards = new_cards.filter(deck_id=deck_id)
    elif level:
        # Filter by level (match deck level, not word level)
        new_cards = new_cards.filter(deck__level=level)
    else:
        # Default to user's current level
        user_level = getattr(user, 'current_level', 'A1')
        new_cards = new_cards.filter(deck__level=user_level)
    
    # Calculate mix: 70% due, 30% new
    due_count = int(limit * 0.7)
    
    # Get due cards
    due_cards = [p.flashcard for p in due_progress[:due_count]]
    actual_due = len(due_cards)
    
    # Calculate how many new cards we need
    # If we have fewer due cards than expected, get more new cards to compensate
    needed_new = limit - actual_due
    
    # Get new cards - ensure we get enough
    new_card_queryset = new_cards.order_by('?')  # Random order
    new_card_list = list(new_card_queryset[:needed_new])
    
    # Combine and shuffle
    selected_cards = due_cards + new_card_list
    random.shuffle(selected_cards)
    
    # Ensure we have exactly 'limit' cards (or as many as available)
    return selected_cards[:limit]


def calculate_daily_progress(user):
    """
    Calculate user's progress for today.
    
    Args:
        user: User instance
    
    Returns:
        dict: Daily progress statistics
    """
    from .models import UserFlashcardProgress, StudySession
    from django.utils import timezone
    from django.db.models import Sum
    
    today = timezone.now().date()
    
    # Get today's sessions
    sessions_today = StudySession.objects.filter(
        user=user,
        started_at__date=today
    )
    
    # Calculate stats
    cards_learned = sessions_today.aggregate(
        total=Sum('cards_studied')
    )['total'] or 0
    
    time_spent = sessions_today.aggregate(
        total=Sum('time_spent_seconds')
    )['total'] or 0
    
    # Get user's goal (default: 20) - UserProfile doesn't have daily_goal yet
    daily_goal = 20
    
    return {
        'cards_today': cards_learned,
        'daily_goal': daily_goal,
        'progress_percentage': min(100, int((cards_learned / daily_goal) * 100)) if daily_goal > 0 else 0,
        'time_spent_minutes': int(time_spent / 60),
        'is_goal_reached': cards_learned >= daily_goal
    }


def update_user_streak(user):
    """
    Update user's streak based on study activity.
    
    Rules:
    - Streak continues if user studied today or yesterday
    - Streak breaks if user missed more than 1 day
    
    Args:
        user: User instance
    
    Returns:
        dict: Updated streak information
    """
    from django.utils import timezone
    
    today = timezone.now().date()
    last_study = user.last_study_date
    
    # First time studying
    if not last_study:
        user.streak_days = 1
        user.longest_streak = 1
        user.last_study_date = today
        user.save()
        return {
            'current': 1,
            'longest': 1,
            'updated': True
        }
    
    # Already studied today
    if last_study == today:
        return {
            'current': user.streak_days,
            'longest': user.longest_streak,
            'updated': False
        }
    
    # Calculate days difference
    days_diff = (today - last_study).days
    
    if days_diff == 1:
        # Continue streak
        user.streak_days += 1
        if user.streak_days > user.longest_streak:
            user.longest_streak = user.streak_days
        user.last_study_date = today
        user.save()
        
        return {
            'current': user.streak_days,
            'longest': user.longest_streak,
            'updated': True,
            'increased': True
        }
    else:
        # Streak broken
        old_streak = user.streak_days
        user.streak_days = 1
        user.last_study_date = today
        user.save()
        
        return {
            'current': 1,
            'longest': user.longest_streak,
            'updated': True,
            'broken': True,
            'previous_streak': old_streak
        }


def get_difficult_cards(user, deck_id=None, limit=20):
    """
    Get cards with low easiness factor (< 2.5 = difficult).
    
    Args:
        user: User object
        deck_id: Optional deck to filter by
        limit: Max number of cards to return
    
    Returns:
        QuerySet of Flashcard objects
    """
    from .models import UserFlashcardProgress, Flashcard
    
    # Get progress entries with low easiness factor
    progress_qs = UserFlashcardProgress.objects.filter(
        user=user,
        easiness_factor__lt=2.5,
        is_mastered=False  # Don't include mastered cards
    ).select_related('flashcard', 'flashcard__word', 'flashcard__deck')
    
    if deck_id:
        progress_qs = progress_qs.filter(flashcard__deck_id=deck_id)
    
    # Order by difficulty (lowest easiness first)
    progress_qs = progress_qs.order_by('easiness_factor', '-total_reviews')
    
    # Extract flashcards
    flashcard_ids = [p.flashcard_id for p in progress_qs[:limit]]
    return Flashcard.objects.filter(id__in=flashcard_ids).select_related('word', 'deck')


def get_failed_cards(user, deck_id=None, limit=20):
    """
    Get cards rated as "Again" (interval reset to 0).
    
    Args:
        user: User object
        deck_id: Optional deck to filter by
        limit: Max number of cards to return
    
    Returns:
        QuerySet of Flashcard objects
    """
    from .models import UserFlashcardProgress, Flashcard
    
    # Get progress entries with failed attempts
    progress_qs = UserFlashcardProgress.objects.filter(
        user=user,
        interval=0,  # Failed cards have 0 interval
        is_learning=True,
        is_mastered=False
    ).select_related('flashcard', 'flashcard__word', 'flashcard__deck')
    
    if deck_id:
        progress_qs = progress_qs.filter(flashcard__deck_id=deck_id)
    
    # Order by total reviews (most reviewed = most failed)
    progress_qs = progress_qs.order_by('-total_reviews', 'easiness_factor')
    
    # Extract flashcards
    flashcard_ids = [p.flashcard_id for p in progress_qs[:limit]]
    return Flashcard.objects.filter(id__in=flashcard_ids).select_related('word', 'deck')


def get_due_cards(user, deck_id=None, limit=20):
    """
    Get cards that are due for review today.
    
    Args:
        user: User object
        deck_id: Optional deck to filter by
        limit: Max number of cards to return
    
    Returns:
        QuerySet of Flashcard objects
    """
    from django.utils import timezone
    from .models import UserFlashcardProgress, Flashcard
    
    today = timezone.now().date()
    
    # Get progress entries due for review
    progress_qs = UserFlashcardProgress.objects.filter(
        user=user,
        next_review_date__lte=today,
        is_mastered=False
    ).select_related('flashcard', 'flashcard__word', 'flashcard__deck')
    
    if deck_id:
        progress_qs = progress_qs.filter(flashcard__deck_id=deck_id)
    
    # Order by next review date (most overdue first)
    progress_qs = progress_qs.order_by('next_review_date', 'easiness_factor')
    
    # Extract flashcards
    flashcard_ids = [p.flashcard_id for p in progress_qs[:limit]]
    return Flashcard.objects.filter(id__in=flashcard_ids).select_related('word', 'deck')


def get_tagged_cards(user, tag, deck_id=None, limit=20):
    """
    Get cards with a specific user tag.
    
    Args:
        user: User object
        tag: Tag name ('difficult', 'review_later', 'important', 'mastered')
        deck_id: Optional deck to filter by
        limit: Max number of cards to return
    
    Returns:
        QuerySet of Flashcard objects
    """
    from .models_study_tracking import UserCardTag
    from .models import Flashcard
    
    # Get tagged cards
    tags_qs = UserCardTag.objects.filter(
        user=user,
        tag=tag
    ).select_related('flashcard', 'flashcard__word', 'flashcard__deck')
    
    if deck_id:
        tags_qs = tags_qs.filter(flashcard__deck_id=deck_id)
    
    # Order by most recently tagged
    tags_qs = tags_qs.order_by('-created_at')
    
    # Extract flashcards
    flashcard_ids = [t.flashcard_id for t in tags_qs[:limit]]
    return Flashcard.objects.filter(id__in=flashcard_ids).select_related('word', 'deck')
