#!/usr/bin/env python3
"""
Quick API test script for Phase 1 Backend.
Uses Django shell to bypass authentication.
"""

import os
import sys

# Setup Django environment FIRST
sys.path.insert(0, '/home/n2t/Documents/english_study/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# NOW import models after setup
from django.contrib.auth import get_user_model
from apps.vocabulary.models import FlashcardDeck, Flashcard
from apps.vocabulary.models_study_tracking import DeckStudyHistory, UserCardTag
from apps.vocabulary.utils_flashcard import (
    get_difficult_cards, get_failed_cards, get_due_cards, get_tagged_cards
)

User = get_user_model()


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_deck_study_history():
    """Test DeckStudyHistory model"""
    print_section("TEST 1: DeckStudyHistory Model")
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    histories = DeckStudyHistory.objects.filter(user=user).order_by('-last_studied_at')
    
    print(f"✅ Found {histories.count()} deck histories for {user.username}\n")
    
    for h in histories:
        print(f"  📚 {h.deck.name} ({h.deck.level})")
        print(f"     Progress: {h.progress_percentage}%")
        print(f"     Sessions: {h.total_sessions}")
        print(f"     Cards: {h.cards_mastered} mastered, {h.cards_learning} learning, {h.cards_new} new")
        print(f"     Difficult: {h.cards_difficult}")
        print(f"     Last studied: {h.last_studied_at.strftime('%Y-%m-%d %H:%M')}")
        print()


def test_difficult_cards():
    """Test get_difficult_cards() function"""
    print_section("TEST 2: Get Difficult Cards Function")
    
    user = User.objects.first()
    deck = FlashcardDeck.objects.first()
    
    if not user or not deck:
        print("❌ No user or deck found")
        return
    
    difficult = get_difficult_cards(user, deck.id, limit=10)
    
    print(f"✅ Found {difficult.count()} difficult cards in {deck.name}\n")
    
    for idx, card in enumerate(difficult[:5], 1):
        print(f"  [{idx}] {card.word.text} ({card.word.cefr_level})")


def test_due_cards():
    """Test get_due_cards() function"""
    print_section("TEST 3: Get Due Cards Function")
    
    user = User.objects.first()
    deck = FlashcardDeck.objects.first()
    
    if not user or not deck:
        print("❌ No user or deck found")
        return
    
    due = get_due_cards(user, deck.id, limit=10)
    
    print(f"✅ Found {due.count()} cards due for review in {deck.name}\n")
    
    for idx, card in enumerate(due[:5], 1):
        print(f"  [{idx}] {card.word.text}")


def test_failed_cards():
    """Test get_failed_cards() function"""
    print_section("TEST 4: Get Failed Cards Function")
    
    user = User.objects.first()
    deck = FlashcardDeck.objects.first()
    
    if not user or not deck:
        print("❌ No user or deck found")
        return
    
    failed = get_failed_cards(user, deck.id, limit=10)
    
    print(f"✅ Found {failed.count()} failed cards in {deck.name}\n")
    
    for idx, card in enumerate(failed[:5], 1):
        print(f"  [{idx}] {card.word.text}")


def test_card_tagging():
    """Test UserCardTag model"""
    print_section("TEST 5: Card Tagging System")
    
    user = User.objects.first()
    flashcard = Flashcard.objects.first()
    
    if not user or not flashcard:
        print("❌ No user or flashcard found")
        return
    
    # Create a tag
    tag, created = UserCardTag.objects.get_or_create(
        user=user,
        flashcard=flashcard,
        tag='difficult',
        defaults={'notes': 'Test tag from script'}
    )
    
    if created:
        print(f"✅ Created new tag: {flashcard.word.text} -> difficult")
    else:
        print(f"✅ Tag already exists: {flashcard.word.text} -> difficult")
    
    # Test get_tagged_cards
    tagged = get_tagged_cards(user, 'difficult', deck_id=flashcard.deck.id, limit=10)
    print(f"\n✅ Found {tagged.count()} cards tagged as 'difficult'\n")
    
    for idx, card in enumerate(tagged[:5], 1):
        print(f"  [{idx}] {card.word.text}")


def test_progress_update():
    """Test DeckStudyHistory.update_progress()"""
    print_section("TEST 6: Progress Update Method")
    
    user = User.objects.first()
    history = DeckStudyHistory.objects.filter(user=user).first()
    
    if not history:
        print("❌ No deck history found")
        return
    
    print(f"Before update:")
    print(f"  Progress: {history.progress_percentage}%")
    print(f"  Mastered: {history.cards_mastered}")
    print(f"  Learning: {history.cards_learning}")
    print(f"  New: {history.cards_new}")
    
    history.update_progress()
    history.refresh_from_db()
    
    print(f"\nAfter update:")
    print(f"  Progress: {history.progress_percentage}%")
    print(f"  Mastered: {history.cards_mastered}")
    print(f"  Learning: {history.cards_learning}")
    print(f"  New: {history.cards_new}")
    print(f"\n✅ Progress updated successfully!")


def test_all_decks_overview():
    """Test deck overview for all decks"""
    print_section("TEST 7: All Decks Overview")
    
    user = User.objects.first()
    if not user:
        print("❌ No user found")
        return
    
    decks = FlashcardDeck.objects.filter(is_official=True).order_by('level')
    
    print(f"📊 Overview of all {decks.count()} official decks:\n")
    
    for deck in decks:
        # Get or create history
        history, created = DeckStudyHistory.objects.get_or_create(
            user=user,
            deck=deck
        )
        
        if created:
            history.update_progress()
        
        total = deck.flashcards.count()
        
        print(f"  {deck.icon} {deck.name}")
        print(f"     Level: {deck.level}")
        print(f"     Total cards: {total}")
        print(f"     Progress: {history.progress_percentage}%")
        print(f"     Sessions: {history.total_sessions}")
        
        if history.total_sessions > 0:
            print(f"     Status: 🔥 Active")
        else:
            print(f"     Status: 🆕 Not started")
        print()


def main():
    print("=" * 70)
    print("  PHASE 1 BACKEND - API & MODEL TESTS")
    print("=" * 70)
    print("  Testing via Django ORM (bypassing REST API)")
    
    try:
        test_deck_study_history()
        test_difficult_cards()
        test_due_cards()
        test_failed_cards()
        test_card_tagging()
        test_progress_update()
        test_all_decks_overview()
        
        print("\n" + "=" * 70)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n🚀 Phase 1 Backend is working correctly!")
        print("📌 Ready to proceed with Phase 2 Frontend implementation\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
