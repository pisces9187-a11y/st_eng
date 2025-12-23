"""
Vocabulary API URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import vocabulary_api

app_name = 'vocabulary'

router = DefaultRouter()
router.register(r'words', vocabulary_api.WordViewSet, basename='word')
router.register(r'decks', vocabulary_api.FlashcardDeckViewSet, basename='deck')
router.register(r'progress', vocabulary_api.FlashcardProgressViewSet, basename='progress')
router.register(r'sessions', vocabulary_api.StudySessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
