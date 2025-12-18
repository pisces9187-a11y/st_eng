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

# Import API views
from .api import discrimination_api, production_api, dashboard_api

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
    
    # =========================================================================
    # DISCRIMINATION PRACTICE API (Days 6-7)
    # =========================================================================
    path('discrimination/sessions/start/', discrimination_api.start_session, name='discrimination-start'),
    path('discrimination/attempts/submit/', discrimination_api.submit_attempt, name='discrimination-submit'),
    path('discrimination/sessions/<str:session_id>/', discrimination_api.get_session, name='discrimination-session'),
    path('discrimination/sessions/<str:session_id>/complete/', discrimination_api.complete_session, name='discrimination-complete'),
    path('discrimination/sessions/history/', discrimination_api.get_history, name='discrimination-history'),
    
    # =========================================================================
    # PRODUCTION RECORDING API (Days 8-9)
    # =========================================================================
    path('production/recordings/upload/', production_api.upload_recording, name='production-upload'),
    path('production/recordings/', production_api.list_recordings, name='production-list'),
    path('production/recordings/<int:recording_id>/', production_api.get_recording_detail, name='production-detail'),
    path('production/recordings/<int:recording_id>/update/', production_api.update_recording, name='production-update'),
    path('production/recordings/<int:recording_id>/delete/', production_api.delete_recording, name='production-delete'),
    path('production/phonemes/<int:phoneme_id>/recordings/', production_api.get_phoneme_recordings, name='production-phoneme-recordings'),
    
    # =========================================================================
    # LEARNING HUB DASHBOARD API (Day 10)
    # =========================================================================
    path('dashboard/stats/', dashboard_api.get_dashboard_stats, name='dashboard-stats'),
    path('dashboard/recommendations/', dashboard_api.get_recommendations, name='dashboard-recommendations'),
    path('dashboard/activity/', dashboard_api.get_recent_activity, name='dashboard-activity'),
    path('dashboard/progress-chart/', dashboard_api.get_progress_chart_data, name='dashboard-progress-chart'),
]
