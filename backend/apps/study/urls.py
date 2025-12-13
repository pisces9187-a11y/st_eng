"""
URL configuration for Study app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserCourseEnrollmentViewSet, UserLessonProgressViewSet,
    FlashcardSRSViewSet, PracticeSessionViewSet,
    DailyStreakViewSet, LearningGoalViewSet,
    DashboardView, StudyStatsView
)

app_name = 'study'

router = DefaultRouter()
router.register(r'enrollments', UserCourseEnrollmentViewSet, basename='enrollment')
router.register(r'progress/lessons', UserLessonProgressViewSet, basename='lesson-progress')
router.register(r'srs/flashcards', FlashcardSRSViewSet, basename='srs-flashcard')
router.register(r'practice/sessions', PracticeSessionViewSet, basename='practice-session')
router.register(r'streaks', DailyStreakViewSet, basename='streak')
router.register(r'goals', LearningGoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard & Stats
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('stats/', StudyStatsView.as_view(), name='stats'),
]
