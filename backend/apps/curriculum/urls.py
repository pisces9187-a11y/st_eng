"""
URL configuration for Curriculum app.

This app manages:
- Courses, Units, Lessons (Grammar, Vocabulary A1-C1)
- Pronunciation Learning (Phonemes, IPA)
- Text-to-Speech (TTS)
- Flashcards, Grammar Rules

URL Structure:
- Page URLs: Exported as `page_urlpatterns` for main urls.py (namespace='curriculum')
- API URLs: Exported as `urlpatterns` for /api/v1/ (namespace='curriculum')
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# API Views
from .views import (
    CourseViewSet, UnitViewSet, LessonViewSet,
    SentenceViewSet, FlashcardViewSet, GrammarRuleViewSet
)

from .views_tts import (
    TTSSpeakView, TTSPhonemeView, TTSVoicesView, TTSStatusView
)

from .views_pronunciation import (
    PronunciationLessonListView,
    PronunciationLessonDetailView,
    SaveScreenProgressView,
    SaveChallengeResultView,
    CompleteLessonView,
    UserPronunciationProgressView,
    PhonemeListWithProgressView,
)

# Template Views (for page URLs)
from .template_views import (
    PronunciationLibraryView, PronunciationLessonView,
    PhonemeChartView, PronunciationProgressView,
    LessonLibraryView, LessonPlayerView
)

# Note: app_name is used for API URLs namespace
# Page URLs will get namespace via include() in main urls.py
app_name = 'curriculum'

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'sentences', SentenceViewSet, basename='sentence')
router.register(r'flashcards', FlashcardViewSet, basename='flashcard')
router.register(r'grammar', GrammarRuleViewSet, basename='grammar')


# =========================================================================
# PAGE URLs (Django Template Views) - Exported for main urls.py
# These will be included with namespace='curriculum' in config/urls.py
# Usage in templates: {% url 'curriculum:pronunciation-library' %}
# =========================================================================
page_urlpatterns = [
    # Pronunciation Learning Pages
    path('pronunciation/', PronunciationLibraryView.as_view(), name='pronunciation-library'),
    path('pronunciation/chart/', PhonemeChartView.as_view(), name='phoneme-chart'),
    path('pronunciation/progress/', PronunciationProgressView.as_view(), name='pronunciation-progress'),
    path('pronunciation/lesson/<slug:slug>/', PronunciationLessonView.as_view(), name='pronunciation-lesson'),
    
    # Lesson Library Pages (Grammar, Vocabulary A1-C1)
    path('lessons/', LessonLibraryView.as_view(), name='lesson-library'),
    path('lessons/<slug:slug>/', LessonPlayerView.as_view(), name='lesson-player'),
]


# =========================================================================
# API URLs (REST API Endpoints)
# These will be included under /api/v1/ with namespace='curriculum'
# =========================================================================
urlpatterns = [
    path('', include(router.urls)),
    
    # TTS API endpoints
    path('tts/speak/', TTSSpeakView.as_view(), name='tts-speak'),
    path('tts/phoneme/', TTSPhonemeView.as_view(), name='tts-phoneme'),
    path('tts/voices/', TTSVoicesView.as_view(), name='tts-voices'),
    path('tts/status/', TTSStatusView.as_view(), name='tts-status'),
    
    # Pronunciation Learning API endpoints
    path('pronunciation/lessons/', PronunciationLessonListView.as_view(), name='pronunciation-lessons'),
    path('pronunciation/lessons/<slug:slug>/', PronunciationLessonDetailView.as_view(), name='pronunciation-lesson-detail'),
    path('pronunciation/progress/', UserPronunciationProgressView.as_view(), name='api-pronunciation-progress'),
    path('pronunciation/progress/screen/', SaveScreenProgressView.as_view(), name='pronunciation-screen-progress'),
    path('pronunciation/progress/challenge/', SaveChallengeResultView.as_view(), name='pronunciation-challenge'),
    path('pronunciation/progress/complete/', CompleteLessonView.as_view(), name='pronunciation-complete'),
    path('pronunciation/phonemes/', PhonemeListWithProgressView.as_view(), name='pronunciation-phonemes'),
]

