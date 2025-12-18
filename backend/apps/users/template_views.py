"""
Template Views for Users App.
These views render the frontend templates for auth and profile flows.
"""

from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .middleware import JWTRequiredMixin


# =========================================================================
# PUBLIC PAGE VIEWS (No authentication required)
# =========================================================================

class HomePageView(TemplateView):
    """
    Render home/landing page template.
    If user is already authenticated, redirect to dashboard.
    """
    template_name = 'pages/home.html'
    
    def dispatch(self, request, *args, **kwargs):
        # If user is authenticated via JWT, redirect to dashboard
        if getattr(request, 'jwt_authenticated', False):
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)


# =========================================================================
# AUTHENTICATION PAGE VIEWS (Only for guests)
# =========================================================================

class LoginPageView(TemplateView):
    """
    Render login page template.
    If user is already authenticated, redirect to dashboard.
    """
    template_name = 'users/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is already logged in via JWT
        if getattr(request, 'jwt_authenticated', False):
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)


class SignupPageView(TemplateView):
    """
    Render signup page template with email verification flow.
    """
    template_name = 'users/signup.html'
    
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, 'jwt_authenticated', False):
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)


class ForgotPasswordPageView(TemplateView):
    """
    Render forgot password page template.
    Handles both:
    - Initial request (enter email)
    - Password reset with token (from email link)
    """
    template_name = 'users/forgot_password.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass reset token if present in URL
        context['reset_token'] = self.request.GET.get('token', '')
        return context


class LogoutPageView(TemplateView):
    """
    Render logout confirmation page.
    The actual logout logic is handled by JavaScript.
    """
    template_name = 'users/logout.html'


class PasswordResetConfirmPageView(TemplateView):
    """
    Redirect old password reset confirm URLs to the new page with token.
    """
    template_name = 'users/forgot_password.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reset_token'] = kwargs.get('token', '')
        return context


# =========================================================================
# DASHBOARD & ONBOARDING PAGE VIEWS (Requires authentication)
# =========================================================================

class DashboardPageView(JWTRequiredMixin, TemplateView):
    """
    Render user dashboard page.
    Requires JWT authentication - redirects to login if not authenticated.
    """
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Dashboard'
        context['user'] = self.request.jwt_user
        return context


class OnboardingPageView(JWTRequiredMixin, TemplateView):
    """
    Render onboarding page for new users.
    Requires JWT authentication.
    """
    template_name = 'users/onboarding.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Thiết lập tài khoản'
        context['user'] = self.request.jwt_user
        return context


# =========================================================================
# PROFILE PAGE VIEWS (Requires authentication)
# =========================================================================

class ProfilePageView(JWTRequiredMixin, TemplateView):
    """
    Render user profile page.
    Shows user info, stats, and learning progress.
    """
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Hồ sơ của tôi'
        context['user'] = self.request.jwt_user
        return context


class ProfileSettingsPageView(JWTRequiredMixin, TemplateView):
    """
    Render profile settings page.
    Allows user to update personal info and preferences.
    """
    template_name = 'users/profile_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Cài đặt hồ sơ'
        context['user'] = self.request.jwt_user
        return context


class ChangePasswordPageView(JWTRequiredMixin, TemplateView):
    """
    Render change password page.
    Requires current password verification.
    """
    template_name = 'users/change_password.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Đổi mật khẩu'
        context['user'] = self.request.jwt_user
        return context


class AchievementsPageView(JWTRequiredMixin, TemplateView):
    """
    Render achievements page.
    Shows all available and unlocked achievements.
    """
    template_name = 'users/achievements.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Thành tựu'
        context['user'] = self.request.jwt_user
        return context


class SubscriptionPageView(JWTRequiredMixin, TemplateView):
    """
    Render subscription management page.
    Shows current plan and upgrade options.
    """
    template_name = 'users/subscription.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Gói đăng ký'
        context['user'] = self.request.jwt_user
        return context


# =========================================================================
# PUBLIC COMMUNITY PAGE VIEWS
# =========================================================================

class ForumPageView(TemplateView):
    """
    Render community forum page.
    """
    template_name = 'pages/forum.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Diễn đàn cộng đồng'
        return context


class LeaderboardPageView(TemplateView):
    """
    Render leaderboard page showing top learners.
    """
    template_name = 'pages/leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Bảng xếp hạng'
        return context


class HelpCenterPageView(TemplateView):
    """
    Render help center / support page.
    """
    template_name = 'pages/help_center.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Trung tâm hỗ trợ'
        return context


class ClearAuthView(TemplateView):
    """
    Clear authentication cookies and redirect to login.
    Use this if user has expired tokens stuck in browser.
    """
    template_name = 'users/login.html'
    
    def get(self, request, *args, **kwargs):
        response = redirect('users:login')
        response.delete_cookie('access_token', samesite='Lax')
        response.delete_cookie('refresh_token', samesite='Lax')
        return response
