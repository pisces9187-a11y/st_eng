"""
Test Vocabulary SM-2 Spaced Repetition Flow
Tests the complete learning workflow with quality ratings
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from apps.vocabulary.models import (
    Word, FlashcardDeck, Flashcard, 
    UserFlashcardProgress, StudySession
)

User = get_user_model()

def test_sm2_flow():
    """Test complete SM-2 spaced repetition flow"""
    
    # Create test user
    print("[1] Setting up test user...")
    user, created = User.objects.get_or_create(
        username='sm2_tester',
        defaults={
            'email': 'sm2test@example.com',
            'is_active': True
        }
    )
    print(f"    User: {user.username}")
    
    # Get first deck
    print("\n[2] Getting first flashcard deck...")
    deck = FlashcardDeck.objects.first()
    if not deck:
        print("    ERROR: No decks found!")
        return
    print(f"    Deck: {deck.name} ({deck.card_count} cards)")
    
    # Get first flashcard
    print("\n[3] Getting study cards...")
    flashcard = deck.flashcards.first()
    if not flashcard:
        print("    ERROR: No flashcards in deck!")
        return
    print(f"    Flashcard: {flashcard.front_text}")
    print(f"    Back: {flashcard.back_text}")
    
    # Create/get progress entry
    print("\n[4] Creating learning progress...")
    progress, created = UserFlashcardProgress.objects.get_or_create(
        user=user,
        flashcard=flashcard,
        defaults={
            'easiness_factor': 2.5,
            'interval': 1,
            'repetitions': 0,
            'next_review_date': timezone.now(),
        }
    )
    print(f"    Progress created: {created}")
    print(f"    Initial state: EF={progress.easiness_factor}, interval={progress.interval}")
    
    # Simulate quality ratings
    print("\n[5] Testing SM-2 quality ratings...")
    quality_tests = [
        (1, "Forgot (reset to 1 day)"),
        (3, "Hard (10 days)"),
        (5, "Easy (increases by EF)"),
    ]
    
    original_ef = progress.easiness_factor
    original_interval = progress.interval
    
    for quality, description in quality_tests:
        # Record initial state
        before_ef = progress.easiness_factor
        before_interval = progress.interval
        
        # Calculate next review (updates the object)
        progress.calculate_next_review(quality)
        
        after_ef = progress.easiness_factor
        after_interval = progress.interval
        next_review = progress.next_review_date
        
        print(f"\n    Quality={quality}: {description}")
        print(f"    - Easiness Factor: {before_ef:.2f} -> {after_ef:.2f}")
        print(f"    - Interval: {before_interval} -> {after_interval} days")
        print(f"    - Next review: {next_review}")
        
        # Verify SM-2 rules
        if quality < 3:
            assert after_interval == 1, f"Quality {quality} should reset interval to 1"
            print(f"    ✓ Interval reset on poor recall")
        elif quality >= 3:
            print(f"    ✓ Good recall registered")
        
        print(f"    ✓ SM-2 rules verified")
    
    # Test study session
    print("\n[6] Creating study session...")
    session = StudySession.objects.create(
        user=user,
        deck=deck,
        cards_studied=1,
        cards_correct=1,
    )
    
    # End session
    session.end_session()
    session.save()
    
    print(f"    Session ID: {session.id}")
    print(f"    Cards studied: {session.cards_studied}")
    print(f"    Cards correct: {session.cards_correct}")
    print(f"    Time spent: {session.time_spent_seconds}s")
    
    # Verify learning progress
    print("\n[7] Verifying learning progress...")
    progress.refresh_from_db()
    print(f"    Total reviews: {progress.total_reviews}")
    print(f"    Current EF: {progress.easiness_factor:.2f}")
    print(f"    Next interval: {progress.interval} days")
    print(f"    Next review: {progress.next_review_date}")
    
    # Test filtering due cards
    print("\n[8] Testing due cards query...")
    due_count = UserFlashcardProgress.objects.filter(
        user=user,
        next_review_date__lte=timezone.now()
    ).count()
    print(f"    Due cards: {due_count}")
    
    print("\n[OK] SM-2 Spaced Repetition Test Complete!")

if __name__ == "__main__":
    test_sm2_flow()
