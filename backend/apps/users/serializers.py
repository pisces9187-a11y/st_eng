"""
Serializers for Users app.

Handles serialization/deserialization for User, Profile, Settings,
Subscription, and Achievement models.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile, UserSettings, Subscription, Achievement, UserAchievement

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'bio', 'learning_goals', 'interests',
            'occupation', 'country', 'city', 'social_links',
            'onboarding_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for UserSettings model."""
    
    class Meta:
        model = UserSettings
        fields = [
            'id', 'email_notifications', 'push_notifications',
            'study_reminders', 'reminder_time', 'weekly_report',
            'sound_effects', 'auto_play_audio', 'show_ipa', 'show_example',
            'cards_per_session', 'dark_mode', 'language',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    
    is_active = serializers.BooleanField(read_only=True)
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_display', 'status', 'status_display',
            'starts_at', 'expires_at', 'is_auto_renew',
            'payment_method', 'is_active', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'starts_at', 'expires_at',
            'is_active', 'created_at'
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Token serializer that includes user data in response.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to response
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'current_level': user.current_level,
            'xp_points': user.xp_points,
            'streak_days': user.streak_days,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        return data


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested representations."""
    
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'display_name', 'avatar',
            'current_level', 'xp_points'
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Full user serializer with profile and settings."""
    
    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    level_display = serializers.CharField(source='get_current_level_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'current_level', 'level_display', 'xp_points',
            'streak_days', 'longest_streak', 'last_study_date',
            'is_active', 'date_joined', 'last_login',
            'profile', 'settings', 'subscription'
        ]
        read_only_fields = [
            'id', 'xp_points', 'streak_days', 'longest_streak',
            'last_study_date', 'date_joined', 'last_login'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Mật khẩu xác nhận không khớp.'
            })
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email này đã được sử dụng.')
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Mật khẩu xác nhận không khớp.'
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mật khẩu hiện tại không đúng.')
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Không tìm thấy tài khoản với email này.')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Mật khẩu xác nhận không khớp.'
            })
        return attrs


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'code', 'description', 'icon',
            'category', 'category_display',
            'xp_reward', 'badge_image',
            'requirement_type', 'requirement_value',
            'is_secret'
        ]


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for UserAchievement model."""
    
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement', 'progress', 'current_value',
            'is_unlocked', 'unlocked_at', 'created_at'
        ]
        read_only_fields = fields


class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer for leaderboard entries."""
    
    rank = serializers.IntegerField()
    user = UserMinimalSerializer()
    xp_points = serializers.IntegerField()
    streak_days = serializers.IntegerField()
    level = serializers.CharField()


class SocialAuthSerializer(serializers.Serializer):
    """
    Serializer for Social Authentication (Google, Facebook).
    
    Used to validate the access token from the OAuth provider.
    """
    
    access_token = serializers.CharField(
        required=True,
        help_text='OAuth access token from Google or Facebook'
    )
    
    def validate_access_token(self, value):
        if not value or len(value) < 20:
            raise serializers.ValidationError('Access token không hợp lệ.')
        return value


class SendVerificationCodeSerializer(serializers.Serializer):
    """
    Serializer for sending email verification code.
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email này đã được đăng ký.')
        return value.lower()


class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer for verifying email with code.
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    
    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('Mã xác nhận phải là 6 chữ số.')
        return value


class UserRegistrationWithVerificationSerializer(serializers.Serializer):
    """
    Serializer for user registration after email verification.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    full_name = serializers.CharField(required=True, max_length=150)
    
    def validate_email(self, value):
        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Email này đã được đăng ký.')
        return value.lower()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Mật khẩu xác nhận không khớp.'
            })
        return attrs
    
    def create(self, validated_data):
        email = validated_data['email']
        full_name = validated_data['full_name']
        
        # Tạo username từ email
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Tách full_name thành first_name và last_name
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
        return user
