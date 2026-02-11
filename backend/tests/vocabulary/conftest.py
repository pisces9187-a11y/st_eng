"""
Vocabulary app specific test fixtures
"""
import pytest
from apps.vocabulary.models import Word, FlashcardDeck, Flashcard, UserFlashcardProgress
from django.utils import timezone


@pytest.fixture
def word_a1(db):
    """Create a test A1 word"""
    return Word.objects.create(
        text='hello',
        pos='noun',
        cefr_level='A1',
        ipa='/həˈləʊ/',
        meaning_en='a greeting',
    )


@pytest.fixture
def flashcard_deck(db):
    """Create a test flashcard deck"""
    return FlashcardDeck.objects.create(
        name='Test Deck A1',
        category='oxford',
        level='A1',
        is_official=True,
        is_public=True,
        icon='📗',
        color='#4CAF50',
    )


@pytest.fixture
def flashcard(db, flashcard_deck, word_a1):
    """Create a test flashcard"""
    return Flashcard.objects.create(
        deck=flashcard_deck,
        word=word_a1,
        front_text='hello',
        back_text='a greeting',
        difficulty=1,
    )


@pytest.fixture
def user_progress(db, user, flashcard):
    """Create user flashcard progress"""
    return UserFlashcardProgress.objects.create(
        user=user,
        flashcard=flashcard,
        easiness_factor=2.5,
        interval=1,
        repetitions=0,
        next_review_date=timezone.now(),
    )
