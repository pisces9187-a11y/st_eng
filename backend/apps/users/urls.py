"""
URL configuration for Users app.

This app manages:
- Authentication (Login, Logout, Register, Password Reset)
- User Profiles and Settings
- Achievements and Subscriptions
- Community Features (Forum, Leaderboard)

URL Structure:
- Page URLs: Exported as `page_urlpatterns` for main urls.py (namespace='users')
- API URLs: Exported as `urlpatterns` for /api/v1/users/
- Auth URLs: Exported as `auth_urlpatterns` for /api/v1/auth/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView, LogoutView,
    UserRegistrationView, UserMeView, UserProfileView, UserSettingsView,
    PasswordChangeView, PasswordResetRequestView, PasswordResetConfirmView,
    SubscriptionView, AchievementViewSet, UserAchievementViewSet,
    LeaderboardView, UserPublicProfileView,
    GoogleAuthView, FacebookAuthView,
    SendVerificationCodeView, VerifyEmailCodeView, RegisterWithVerificationView,
    AvatarUploadView, AvatarDeleteView
)

from .template_views import (
    HomePageView,
    LoginPageView, SignupPageView, ForgotPasswordPageView,
    LogoutPageView, PasswordResetConfirmPageView,
    DashboardPageView, OnboardingPageView,
    ProfilePageView, ProfileSettingsPageView, ChangePasswordPageView,
    AchievementsPageView, SubscriptionPageView,
    ForumPageView, LeaderboardPageView, HelpCenterPageView,
    ClearAuthView
)

# Note: Curriculum template views are now in curriculum/urls.py
# Each app manages its own page URLs for better organization

# Note: app_name is removed here because page_urlpatterns are included 
# with explicit namespace='users' in main urls.py
# app_name = 'users'

router = DefaultRouter()
router.register(r'achievements', AchievementViewSet, basename='achievement')

# =========================================================================
# PAGE URLs (Django Template Views) - Exported for main urls.py
# Note: Don't use 'users:' prefix here, namespace is added via include()
# =========================================================================
page_urlpatterns = [
    # Home/Landing Page
    path('', HomePageView.as_view(), name='home'),
    
    # Authentication Pages
    path('login/', LoginPageView.as_view(), name='login'),
    path('signup/', SignupPageView.as_view(), name='signup'),
    path('forgot-password/', ForgotPasswordPageView.as_view(), name='forgot-password'),
    path('logout/', LogoutPageView.as_view(), name='logout'),
    path('clear-auth/', ClearAuthView.as_view(), name='clear-auth'),  # Clear expired tokens
    path('delete-account/', LogoutPageView.as_view(), name='delete_account'),
    path('reset-password/<str:token>/', PasswordResetConfirmPageView.as_view(), name='reset-password-confirm'),
    
    # User Dashboard & Onboarding
    path('dashboard/', DashboardPageView.as_view(), name='dashboard'),
    path('onboarding/', OnboardingPageView.as_view(), name='onboarding'),
    
    # Profile & Settings Pages
    path('profile/', ProfilePageView.as_view(), name='profile'),
    path('profile-update/', ProfilePageView.as_view(), name='update_profile'),
    path('profile/settings/', ProfileSettingsPageView.as_view(), name='profile-settings'),
    path('profile/change-password/', ChangePasswordPageView.as_view(), name='change-password'),
    path('profile/achievements/', AchievementsPageView.as_view(), name='profile-achievements'),
    path('profile/subscription/', SubscriptionPageView.as_view(), name='profile-subscription'),
    
    # Community Pages
    path('forum/', ForumPageView.as_view(), name='forum'),
    path('leaderboard/', LeaderboardPageView.as_view(), name='leaderboard'),
    path('help/', HelpCenterPageView.as_view(), name='help-center'),
    
    # Note: Pronunciation and Lesson pages are now in curriculum app
    # Access via namespace 'curriculum': {% url 'curriculum:pronunciation-library' %}
]

# =========================================================================
# API URLs (REST API Endpoints)
# =========================================================================
urlpatterns = [
    # Router URLs (achievements)
    path('', include(router.urls)),
    
    # User profile API endpoints
    path('me/', UserMeView.as_view(), name='me'),
    path('me/avatar/', AvatarUploadView.as_view(), name='me-avatar-upload'),
    path('me/profile/', UserProfileView.as_view(), name='me-profile'),
    path('me/settings/', UserSettingsView.as_view(), name='me-settings'),
    path('me/subscription/', SubscriptionView.as_view(), name='me-subscription'),
    path('me/change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('me/achievements/', UserAchievementViewSet.as_view({
        'get': 'list'
    }), name='me-achievements'),
    path('me/achievements/unlocked/', UserAchievementViewSet.as_view({
        'get': 'unlocked'
    }), name='me-achievements-unlocked'),
    path('me/achievements/in-progress/', UserAchievementViewSet.as_view({
        'get': 'in_progress'
    }), name='me-achievements-progress'),
    
    # Public profile
    path('<str:username>/', UserPublicProfileView.as_view(), name='public-profile'),
    
    # Leaderboard
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]

# =========================================================================
# Auth API URLs (to be included in main urls.py under /api/v1/auth/)
# =========================================================================
auth_urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterWithVerificationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Email Verification
    path('send-verification/', SendVerificationCodeView.as_view(), name='send-verification'),
    path('verify-email/', VerifyEmailCodeView.as_view(), name='verify-email'),
    
    # Social Auth
    path('google/', GoogleAuthView.as_view(), name='google-auth'),
    path('facebook/', FacebookAuthView.as_view(), name='facebook-auth'),
]
