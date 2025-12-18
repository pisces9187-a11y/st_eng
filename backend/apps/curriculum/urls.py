"""
URL configuration for Curriculum app.

This app manages:
- Courses, Units, Lessons (Grammar, Vocabulary A1-C1)
- Pronunciation Learning (Phonemes, IPA)
- Text-to-Speech (TTS)
- Phase 1: Audio System (AudioSource, AudioCache)
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

# Phase 1: Audio API Views
from .api_views import (
    PhonemeAudioAPIView,
    PhonemeAudioBulkAPIView,
    SetPreferredAudioAPIView,
    AudioQualityReportAPIView,
    PhonemeAudioURLAPIView
)

# Day 2: Pronunciation Learning Flow API Views
from .api.pronunciation_api import (
    PhonemeDiscoverAPIView,
    PhonemeStartLearningAPIView,
    DiscriminationQuizAPIView,
    DiscriminationSubmitAPIView,
    ProductionReferenceAPIView,
    ProductionSubmitAPIView,
    OverallProgressAPIView,
)

# Template Views (for page URLs)
from .template_views import (
    PronunciationLibraryView, PronunciationLessonView,
    PhonemeChartView, PronunciationProgressView,
    LessonLibraryView, LessonPlayerView,
    PhonemeDetailView, MinimalPairPracticeView
)

# Day 4-5: New Pronunciation Learning Pages
from .views_pronunciation import (
    pronunciation_discovery_view,
    pronunciation_learning_view,
    pronunciation_discrimination_view,
    pronunciation_production_view,
    pronunciation_progress_dashboard_view,
    discrimination_start_view,
    discrimination_quiz_view,
    discrimination_results_view,
    production_record_view,
    production_history_view,
    learning_hub_dashboard_view,
)

# Other Views
from .views import TestAudioView

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
    # Teacher Dashboard (must be BEFORE curriculum paths to avoid conflicts)
    path('teacher-dashboard/', 
         __import__('apps.curriculum.views_teacher', fromlist=['teacher_dashboard']).teacher_dashboard,
         name='teacher-dashboard'),
    
    # Autocomplete URLs (must come before admin URLs)
    path('autocomplete/phoneme/', 
         __import__('apps.curriculum.autocomplete', fromlist=['PhonemeAutocomplete']).PhonemeAutocomplete.as_view(), 
         name='phoneme-autocomplete'),
    
    # Pronunciation Learning Pages
    path('pronunciation/', PronunciationLibraryView.as_view(), name='pronunciation-library'),
    path('pronunciation/chart/', PhonemeChartView.as_view(), name='phoneme-chart'),
    path('pronunciation/phoneme/<str:ipa_symbol>/', PhonemeDetailView.as_view(), name='phoneme-detail'),
    path('pronunciation/minimal-pairs/', MinimalPairPracticeView.as_view(), name='minimal-pair-practice'),
    path('pronunciation/progress/', PronunciationProgressView.as_view(), name='pronunciation-progress'),
    path('pronunciation/lesson/<slug:slug>/', PronunciationLessonView.as_view(), name='pronunciation-lesson'),
    path('test/audio/', TestAudioView.as_view(), name='test-audio'),
    
    # Day 4-5: New Pronunciation Learning Flow Pages (4-Stage Journey)
    path('pronunciation/discovery/', pronunciation_discovery_view, name='pronunciation-discovery'),
    path('pronunciation/learning/<int:phoneme_id>/', pronunciation_learning_view, name='pronunciation-learning'),
    path('pronunciation/discrimination/<int:phoneme_id>/', pronunciation_discrimination_view, name='pronunciation-discrimination'),
    path('pronunciation/production/<int:phoneme_id>/', pronunciation_production_view, name='pronunciation-production'),
    path('pronunciation/dashboard/', pronunciation_progress_dashboard_view, name='pronunciation-dashboard'),
    
    # Day 6-7: Discrimination Quiz Pages
    path('discrimination/start/', discrimination_start_view, name='discrimination-start'),
    path('discrimination/quiz/<str:session_id>/', discrimination_quiz_view, name='discrimination-quiz'),
    path('discrimination/results/<str:session_id>/', discrimination_results_view, name='discrimination-results'),
    
    # Day 8-9: Production Recording Pages
    path('production/record/<int:phoneme_id>/', production_record_view, name='production-record'),
    path('production/history/', production_history_view, name='production-history'),
    
    # Day 10: Learning Hub Dashboard
    path('learning-hub/', learning_hub_dashboard_view, name='learning-hub'),
    
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
    
    # =======================================================================
    # PHASE 1: AUDIO SYSTEM API ENDPOINTS
    # =======================================================================
    
    # Phoneme Audio API
    path('phonemes/<int:phoneme_id>/audio/', 
         PhonemeAudioAPIView.as_view(), 
         name='phoneme-audio'),
    
    path('phonemes/<int:phoneme_id>/audio/url/', 
         PhonemeAudioURLAPIView.as_view(), 
         name='phoneme-audio-url'),
    
    path('phonemes/audio/bulk/', 
         PhonemeAudioBulkAPIView.as_view(), 
         name='phoneme-audio-bulk'),
    
    path('phonemes/<int:phoneme_id>/audio/set-preferred/', 
         SetPreferredAudioAPIView.as_view(), 
         name='phoneme-audio-set-preferred'),
    
    # Audio Quality & Metrics
    path('audio/quality-report/', 
         AudioQualityReportAPIView.as_view(), 
         name='audio-quality-report'),
    
    # =======================================================================
    # TTS API ENDPOINTS
    # =======================================================================
    
    path('tts/speak/', TTSSpeakView.as_view(), name='tts-speak'),
    path('tts/phoneme/', TTSPhonemeView.as_view(), name='tts-phoneme'),
    path('tts/voices/', TTSVoicesView.as_view(), name='tts-voices'),
    path('tts/status/', TTSStatusView.as_view(), name='tts-status'),
    
    # =======================================================================
    # PRONUNCIATION LEARNING API ENDPOINTS
    # =======================================================================
    
    path('pronunciation/lessons/', 
         PronunciationLessonListView.as_view(), 
         name='pronunciation-lessons'),
    
    path('pronunciation/lessons/<slug:slug>/', 
         PronunciationLessonDetailView.as_view(), 
         name='pronunciation-lesson-detail'),
    
    path('pronunciation/progress/', 
         UserPronunciationProgressView.as_view(), 
         name='api-pronunciation-progress'),
    
    path('pronunciation/progress/screen/', 
         SaveScreenProgressView.as_view(), 
         name='pronunciation-screen-progress'),
    
    path('pronunciation/progress/challenge/', 
         SaveChallengeResultView.as_view(), 
         name='pronunciation-challenge'),
    
    path('pronunciation/progress/complete/', 
         CompleteLessonView.as_view(), 
         name='pronunciation-complete'),
    
    path('pronunciation/phonemes/', 
         PhonemeListWithProgressView.as_view(), 
         name='pronunciation-phonemes'),
    
    # =======================================================================
    # DAY 2: PRONUNCIATION LEARNING FLOW API (4-Stage Journey)
    # =======================================================================
    
    # Stage 1: Discovery
    path('pronunciation/phoneme/<int:pk>/discover/', 
         PhonemeDiscoverAPIView.as_view(), 
         name='phoneme-discover'),
    
    # Stage 2: Learning
    path('pronunciation/phoneme/<int:pk>/start-learning/', 
         PhonemeStartLearningAPIView.as_view(), 
         name='phoneme-start-learning'),
    
    # Stage 3: Discrimination Practice
    path('pronunciation/phoneme/<int:pk>/discrimination/quiz/', 
         DiscriminationQuizAPIView.as_view(), 
         name='phoneme-discrimination-quiz'),
    
    path('pronunciation/phoneme/<int:pk>/discrimination/submit/', 
         DiscriminationSubmitAPIView.as_view(), 
         name='phoneme-discrimination-submit'),
    
    # Stage 4: Production Practice
    path('pronunciation/phoneme/<int:pk>/production/reference/', 
         ProductionReferenceAPIView.as_view(), 
         name='phoneme-production-reference'),
    
    path('pronunciation/phoneme/<int:pk>/production/submit/', 
         ProductionSubmitAPIView.as_view(), 
         name='phoneme-production-submit'),
    
    # Overall Progress
    path('pronunciation/progress/overall/', 
         OverallProgressAPIView.as_view(), 
         name='pronunciation-progress-overall'),
]
