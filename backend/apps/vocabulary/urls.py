"""
Vocabulary API URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import vocabulary_api
from .views_flashcard import (
    FlashcardStudyViewSet, FlashcardDeckViewSet, ProgressDashboardViewSet
)
from .views_audio import FlashcardAudioViewSet, get_flashcard_audio

app_name = 'vocabulary'

router = DefaultRouter()

# Original vocabulary API (if exists)
router.register(r'words', vocabulary_api.WordViewSet, basename='word')
router.register(r'decks', vocabulary_api.FlashcardDeckViewSet, basename='deck')
router.register(r'progress', vocabulary_api.FlashcardProgressViewSet, basename='progress')
router.register(r'sessions', vocabulary_api.StudySessionViewSet, basename='session')

# NEW: Flashcard Study API
router.register(r'flashcards/study', FlashcardStudyViewSet, basename='flashcard-study')
router.register(r'flashcards/decks', FlashcardDeckViewSet, basename='flashcard-deck')
router.register(r'flashcards/progress', ProgressDashboardViewSet, basename='flashcard-progress')

# NEW: Audio API
router.register(r'audio', FlashcardAudioViewSet, basename='flashcard-audio')

urlpatterns = [
    path('', include(router.urls)),
    # Flashcard-specific audio endpoint
    path('flashcards/<int:flashcard_id>/audio/', get_flashcard_audio, name='flashcard-audio-detail'),
    # Flashcard tagging endpoint (custom action outside ViewSet)
    path('flashcards/<int:pk>/tag-card/', FlashcardDeckViewSet.as_view({'post': 'tag_card'}), name='flashcard-tag'),
]
