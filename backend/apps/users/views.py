"""
API Views for Users app.

Handles authentication, user profile, settings, subscriptions, and achievements.
"""

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile, UserSettings, Subscription, Achievement, UserAchievement, EmailVerification
from .serializers import (
    UserSerializer, UserMinimalSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserSettingsSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    SubscriptionSerializer, AchievementSerializer, UserAchievementSerializer,
    LeaderboardEntrySerializer, CustomTokenObtainPairSerializer,
    SocialAuthSerializer, SendVerificationCodeSerializer, VerifyEmailSerializer,
    UserRegistrationWithVerificationSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that returns user data along with tokens.
    Sets access_token and refresh_token in HTTP-only cookies.
    
    POST /api/v1/auth/token/
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Set tokens in HTTP-only cookies for better security
        if response.status_code == 200 and 'access' in response.data:
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            
            # Set access token cookie (24 hours)
            response.set_cookie(
                'access_token',
                access_token,
                max_age=86400,  # 24 hours
                httponly=True,
                secure=False,  # Set to True in production (HTTPS only)
                samesite='Lax'
            )
            
            # Set refresh token cookie (30 days)
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=2592000,  # 30 days
                httponly=True,
                secure=False,  # Set to True in production
                samesite='Lax'
            )
        
        return response


class LogoutView(APIView):
    """
    API endpoint for user logout - blacklists refresh token and clears cookies.
    
    POST /api/v1/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Try to blacklist refresh token
            refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    pass  # Token might already be invalid
            
            response = Response({'message': 'Đăng xuất thành công.'}, status=status.HTTP_200_OK)
            
            # Clear authentication cookies
            response.delete_cookie('access_token', samesite='Lax')
            response.delete_cookie('refresh_token', samesite='Lax')
            
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    POST /api/v1/auth/register/
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Đăng ký thành công. Vui lòng đăng nhập.',
            'user': UserMinimalSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class SendVerificationCodeView(APIView):
    """
    API endpoint to send verification code to email.
    
    POST /api/v1/auth/send-verification-code/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Check if email already registered
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create verification code
        verification = EmailVerification.create_verification(email)
        
        # Send email
        try:
            subject = 'Mã xác thực đăng ký - EnglishMaster'
            html_message = f'''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #183B56;">English<span style="color: #F47C26;">Master</span></h1>
                </div>
                <h2 style="color: #183B56;">Xác thực email của bạn</h2>
                <p style="color: #4A4A4A; font-size: 16px;">
                    Chào bạn,<br><br>
                    Cảm ơn bạn đã đăng ký tài khoản EnglishMaster. 
                    Vui lòng sử dụng mã xác thực dưới đây để hoàn tất đăng ký:
                </p>
                <div style="background: #F9FAFC; border-radius: 8px; padding: 30px; text-align: center; margin: 30px 0;">
                    <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #F47C26;">
                        {verification.code}
                    </span>
                </div>
                <p style="color: #6C757D; font-size: 14px;">
                    Mã xác thực có hiệu lực trong <strong>15 phút</strong>.<br>
                    Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.
                </p>
                <hr style="border: none; border-top: 1px solid #E0E0E0; margin: 30px 0;">
                <p style="color: #95A5A6; font-size: 12px; text-align: center;">
                    © 2025 EnglishMaster. All rights reserved.
                </p>
            </body>
            </html>
            '''
            plain_message = f'Mã xác thực của bạn là: {verification.code}. Mã có hiệu lực trong 15 phút.'
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'message': f'Mã xác thực đã được gửi đến {email}. Vui lòng kiểm tra hộp thư.',
                'email': email
            })
            
        except Exception as e:
            # Log error but don't expose details
            print(f'Email send error: {e}')
            return Response(
                {'error': 'Không thể gửi email. Vui lòng thử lại sau.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class VerifyEmailCodeView(APIView):
    """
    API endpoint to verify email code.
    
    POST /api/v1/auth/verify-email/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        # Find verification
        verification = EmailVerification.objects.filter(
            email=email,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not verification:
            return Response(
                {'error': 'Không tìm thấy mã xác thực. Vui lòng yêu cầu mã mới.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code
        success, message = verification.verify(code)
        
        if success:
            return Response({
                'message': message,
                'verified': True,
                'email': email
            })
        else:
            return Response(
                {'error': message, 'verified': False},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterWithVerificationView(APIView):
    """
    API endpoint for user registration with email verification.
    
    POST /api/v1/auth/register/
    
    Requires email to be verified first via send-verification and verify-email.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationWithVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Check if email is verified
        verification = EmailVerification.objects.filter(
            email=email.lower(),
            is_verified=True
        ).order_by('-created_at').first()
        
        if not verification:
            return Response(
                {'error': 'Email chưa được xác thực. Vui lòng xác thực email trước khi đăng ký.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if verification is recent (within 30 minutes)
        from django.utils import timezone
        from datetime import timedelta
        if timezone.now() - verification.verified_at > timedelta(minutes=30):
            return Response(
                {'error': 'Phiên xác thực đã hết hạn. Vui lòng yêu cầu mã xác thực mới.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user using serializer
        try:
            user = serializer.save()
            
            # Clean up verification codes
            EmailVerification.objects.filter(email=email.lower()).delete()
            
            # Generate tokens for auto-login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Đăng ký thành công!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Đã xảy ra lỗi khi tạo tài khoản: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserMeView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for current user profile.
    
    GET /api/v1/users/me/ - Get current user
    PATCH /api/v1/users/me/ - Update current user
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class AvatarUploadView(APIView):
    """
    API endpoint for avatar upload.
    
    POST /api/v1/users/me/avatar/ - Upload avatar
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'Vui lòng chọn file ảnh'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        avatar_file = request.FILES['avatar']
        
        # Validate file type
        if not avatar_file.content_type.startswith('image/'):
            return Response(
                {'error': 'File phải là hình ảnh'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Kích thước file tối đa là 5MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old avatar if exists
        user = request.user
        if user.avatar:
            try:
                user.avatar.delete(save=False)
            except:
                pass
        
        # Save new avatar
        user.avatar = avatar_file
        user.save(update_fields=['avatar'])
        
        return Response({
            'message': 'Cập nhật ảnh đại diện thành công',
            'avatar': user.avatar.url if user.avatar else None
        }, status=status.HTTP_200_OK)


class AvatarDeleteView(APIView):
    """
    API endpoint for avatar deletion.
    
    DELETE /api/v1/users/me/avatar/ - Delete avatar
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        user = request.user
        
        if user.avatar:
            try:
                user.avatar.delete(save=True)
            except:
                pass
        
        return Response({
            'message': 'Đã xóa ảnh đại diện'
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile details.
    
    GET /api/v1/users/me/profile/
    PATCH /api/v1/users/me/profile/
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserSettingsView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user settings.
    
    GET /api/v1/users/me/settings/
    PATCH /api/v1/users/me/settings/
    """
    
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        settings, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return settings


class PasswordChangeView(APIView):
    """
    API endpoint for changing password.
    
    POST /api/v1/users/me/change-password/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return Response({
            'message': 'Đổi mật khẩu thành công.'
        })


class PasswordResetRequestView(APIView):
    """
    API endpoint for requesting password reset.
    
    POST /api/v1/auth/password-reset/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Send password reset email
        # email = serializer.validated_data['email']
        # user = User.objects.get(email=email)
        # send_password_reset_email(user)
        
        return Response({
            'message': 'Nếu email tồn tại, chúng tôi sẽ gửi link đặt lại mật khẩu.'
        })


class PasswordResetConfirmView(APIView):
    """
    API endpoint for confirming password reset.
    
    POST /api/v1/auth/password-reset/confirm/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Validate token and reset password
        # token = serializer.validated_data['token']
        # new_password = serializer.validated_data['new_password']
        
        return Response({
            'message': 'Đặt lại mật khẩu thành công.'
        })


class SubscriptionView(generics.RetrieveAPIView):
    """
    API endpoint for user subscription.
    
    GET /api/v1/users/me/subscription/
    """
    
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        subscription = Subscription.objects.filter(
            user=self.request.user
        ).order_by('-created_at').first()
        
        if not subscription:
            # Create free subscription if none exists
            subscription = Subscription.objects.create(
                user=self.request.user,
                plan='free',
                status='active'
            )
        
        return subscription


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for achievements.
    
    GET /api/v1/achievements/ - List all achievements
    GET /api/v1/achievements/{id}/ - Get achievement detail
    """
    
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Achievement.objects.filter(is_active=True)
        
        # Hide secret achievements that user hasn't unlocked
        if not self.request.user.is_staff:
            unlocked_ids = UserAchievement.objects.filter(
                user=self.request.user,
                is_unlocked=True
            ).values_list('achievement_id', flat=True)
            
            queryset = queryset.filter(
                Q(is_secret=False) | Q(id__in=unlocked_ids)
            )
        
        return queryset.order_by('category', 'order')


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for user achievements.
    
    GET /api/v1/users/me/achievements/ - List user's achievements
    GET /api/v1/users/me/achievements/{id}/ - Get achievement progress
    """
    
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserAchievement.objects.filter(
            user=self.request.user
        ).select_related('achievement').order_by('-unlocked_at', '-created_at')
    
    @action(detail=False, methods=['get'])
    def unlocked(self, request):
        """Get only unlocked achievements."""
        queryset = self.get_queryset().filter(is_unlocked=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_progress(self, request):
        """Get achievements in progress."""
        queryset = self.get_queryset().filter(
            is_unlocked=False,
            progress__gt=0
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LeaderboardView(APIView):
    """
    API endpoint for leaderboard.
    
    GET /api/v1/leaderboard/
    Query params: type (xp, streak), period (daily, weekly, monthly, all)
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        leaderboard_type = request.query_params.get('type', 'xp')
        period = request.query_params.get('period', 'weekly')
        limit = min(int(request.query_params.get('limit', 50)), 100)
        
        # Base queryset
        queryset = User.objects.filter(is_active=True)
        
        # Order by type
        if leaderboard_type == 'streak':
            queryset = queryset.order_by('-streak_days', '-xp_points')
        else:
            queryset = queryset.order_by('-xp_points', '-streak_days')
        
        # TODO: Filter by period using aggregations from study data
        
        users = queryset[:limit]
        
        # Build response
        entries = []
        for rank, user in enumerate(users, 1):
            entries.append({
                'rank': rank,
                'user': UserMinimalSerializer(user).data,
                'xp_points': user.xp_points,
                'streak_days': user.streak_days,
                'level': user.current_level
            })
        
        # Find current user's rank
        current_user_rank = None
        if request.user.is_authenticated:
            for entry in entries:
                if entry['user']['id'] == request.user.id:
                    current_user_rank = entry['rank']
                    break
        
        return Response({
            'type': leaderboard_type,
            'period': period,
            'entries': entries,
            'current_user_rank': current_user_rank
        })


class UserPublicProfileView(generics.RetrieveAPIView):
    """
    API endpoint for viewing other user's public profile.
    
    GET /api/v1/users/{username}/
    """
    
    serializer_class = UserMinimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'
    
    def get_queryset(self):
        return User.objects.filter(is_active=True)


# =============================================================================
# SOCIAL AUTH VIEWS (Google, Facebook)
# =============================================================================

class GoogleAuthView(APIView):
    """
    API endpoint for Google OAuth2 authentication.
    
    POST /api/v1/auth/google/
    
    Frontend sends Google OAuth2 access token, backend verifies with Google
    and creates/authenticates user, returning JWT tokens.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = SocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data['access_token']
        
        try:
            # Verify token with Google
            google_response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if google_response.status_code != 200:
                return Response(
                    {'error': 'Token Google không hợp lệ'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            google_data = google_response.json()
            email = google_data.get('email')
            
            if not email:
                return Response(
                    {'error': 'Không thể lấy email từ Google'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0] + '_google',
                    'first_name': google_data.get('given_name', ''),
                    'last_name': google_data.get('family_name', ''),
                    'is_active': True,
                }
            )
            
            # Update user info if needed
            if not user.first_name and google_data.get('given_name'):
                user.first_name = google_data.get('given_name')
                user.save(update_fields=['first_name'])
            
            if not user.last_name and google_data.get('family_name'):
                user.last_name = google_data.get('family_name')
                user.save(update_fields=['last_name'])
            
            # Download avatar if user doesn't have one
            if not user.avatar and google_data.get('picture'):
                self._save_avatar(user, google_data.get('picture'), 'google')
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'current_level': user.current_level,
                    'xp_points': user.xp_points,
                    'streak_days': user.streak_days,
                    'is_premium': user.is_premium,
                },
                'created': created,
            })
            
        except requests.RequestException as e:
            return Response(
                {'error': f'Lỗi kết nối Google: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def _save_avatar(self, user, avatar_url, provider):
        """Download and save user avatar."""
        try:
            from django.core.files.base import ContentFile
            response = requests.get(avatar_url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                ext = 'png' if 'png' in content_type else 'jpg'
                filename = f'avatar_{user.id}_{provider}.{ext}'
                user.avatar.save(filename, ContentFile(response.content), save=True)
        except Exception:
            pass  # Don't fail auth if avatar download fails


class FacebookAuthView(APIView):
    """
    API endpoint for Facebook OAuth2 authentication.
    
    POST /api/v1/auth/facebook/
    
    Frontend sends Facebook access token, backend verifies with Facebook
    and creates/authenticates user, returning JWT tokens.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = SocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data['access_token']
        
        try:
            # Verify token with Facebook and get user info
            fb_response = requests.get(
                'https://graph.facebook.com/me',
                params={
                    'access_token': access_token,
                    'fields': 'id,name,email,picture.type(large)',
                },
                timeout=10
            )
            
            if fb_response.status_code != 200:
                return Response(
                    {'error': 'Token Facebook không hợp lệ'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            fb_data = fb_response.json()
            email = fb_data.get('email')
            fb_id = fb_data.get('id')
            
            if not email:
                # Facebook might not return email if not verified
                # Use Facebook ID to create a placeholder email
                email = f'{fb_id}@facebook.englishstudy.local'
            
            # Parse name
            name = fb_data.get('name', '')
            name_parts = name.split(' ', 1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': f'fb_{fb_id}',
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                }
            )
            
            # Update user info if needed
            if not user.first_name and first_name:
                user.first_name = first_name
                user.save(update_fields=['first_name'])
            
            if not user.last_name and last_name:
                user.last_name = last_name
                user.save(update_fields=['last_name'])
            
            # Download avatar if user doesn't have one
            if not user.avatar:
                picture_data = fb_data.get('picture', {}).get('data', {})
                avatar_url = picture_data.get('url')
                if avatar_url:
                    self._save_avatar(user, avatar_url, 'facebook')
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'current_level': user.current_level,
                    'xp_points': user.xp_points,
                    'streak_days': user.streak_days,
                    'is_premium': user.is_premium,
                },
                'created': created,
            })
            
        except requests.RequestException as e:
            return Response(
                {'error': f'Lỗi kết nối Facebook: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def _save_avatar(self, user, avatar_url, provider):
        """Download and save user avatar."""
        try:
            from django.core.files.base import ContentFile
            response = requests.get(avatar_url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                ext = 'png' if 'png' in content_type else 'jpg'
                filename = f'avatar_{user.id}_{provider}.{ext}'
                user.avatar.save(filename, ContentFile(response.content), save=True)
        except Exception:
            pass  # Don't fail auth if avatar download fails
