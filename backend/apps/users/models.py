"""
User models for English Learning Platform.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with gamification and learning profile.
    """
    
    class Level(models.TextChoices):
        A1 = 'A1', _('Beginner')
        A2 = 'A2', _('Elementary')
        B1 = 'B1', _('Intermediate')
        B2 = 'B2', _('Upper Intermediate')
        C1 = 'C1', _('Advanced')
        C2 = 'C2', _('Proficient')
    
    # Override email to be required and unique
    email = models.EmailField(_('email address'), unique=True)
    
    # Profile fields
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_('Ảnh đại diện')
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('Số điện thoại')
    )
    
    # Learning profile
    current_level = models.CharField(
        max_length=2,
        choices=Level.choices,
        default=Level.A1,
        verbose_name=_('Trình độ hiện tại')
    )
    target_level = models.CharField(
        max_length=2,
        choices=Level.choices,
        default=Level.B2,
        verbose_name=_('Mục tiêu')
    )
    native_language = models.CharField(
        max_length=50,
        default='Vietnamese',
        verbose_name=_('Ngôn ngữ mẹ đẻ')
    )
    
    # Gamification
    xp_points = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Điểm kinh nghiệm')
    )
    streak_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Chuỗi ngày học')
    )
    longest_streak = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Chuỗi dài nhất')
    )
    last_study_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Ngày học gần nhất')
    )
    
    # Settings
    daily_goal_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name=_('Mục tiêu hàng ngày (phút)')
    )
    timezone = models.CharField(
        max_length=50,
        default='Asia/Ho_Chi_Minh',
        verbose_name=_('Múi giờ')
    )
    
    # Subscription
    is_premium = models.BooleanField(
        default=False,
        verbose_name=_('Tài khoản Premium')
    )
    premium_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Premium hết hạn')
    )
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('Người dùng')
        verbose_name_plural = _('Người dùng')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['current_level']),
            models.Index(fields=['-xp_points']),  # For leaderboard
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def display_name(self):
        return self.get_full_name() or self.username or self.email.split('@')[0]
    
    def add_xp(self, amount: int) -> None:
        """Add XP points to user."""
        self.xp_points += amount
        self.save(update_fields=['xp_points'])
    
    def update_streak(self) -> bool:
        """
        Update study streak. Call this when user completes a study session.
        Returns True if streak was maintained/increased.
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_study_date is None:
            self.streak_days = 1
            self.last_study_date = today
            self.save(update_fields=['streak_days', 'last_study_date'])
            return True
        
        days_diff = (today - self.last_study_date).days
        
        if days_diff == 0:
            # Same day, no change
            return True
        elif days_diff == 1:
            # Consecutive day, increase streak
            self.streak_days += 1
            if self.streak_days > self.longest_streak:
                self.longest_streak = self.streak_days
            self.last_study_date = today
            self.save(update_fields=['streak_days', 'longest_streak', 'last_study_date'])
            return True
        else:
            # Streak broken
            self.streak_days = 1
            self.last_study_date = today
            self.save(update_fields=['streak_days', 'last_study_date'])
            return False


class UserProfile(models.Model):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Người dùng')
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Giới thiệu')
    )
    learning_goals = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Mục tiêu học tập'),
        help_text=_('VD: ["business", "travel", "ielts"]')
    )
    interests = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Sở thích'),
        help_text=_('VD: ["movies", "music", "technology"]')
    )
    occupation = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Nghề nghiệp')
    )
    country = models.CharField(
        max_length=100,
        default='Vietnam',
        verbose_name=_('Quốc gia')
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Thành phố')
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Liên kết mạng xã hội')
    )
    onboarding_completed = models.BooleanField(
        default=False,
        verbose_name=_('Đã hoàn thành onboarding')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Hồ sơ người dùng')
        verbose_name_plural = _('Hồ sơ người dùng')
    
    def __str__(self):
        return f'Profile of {self.user.email}'


class UserSettings(models.Model):
    """
    User preferences and settings.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_('Người dùng')
    )
    
    # Notifications
    email_notifications = models.BooleanField(
        default=True,
        verbose_name=_('Thông báo email')
    )
    push_notifications = models.BooleanField(
        default=True,
        verbose_name=_('Thông báo đẩy')
    )
    study_reminders = models.BooleanField(
        default=True,
        verbose_name=_('Nhắc nhở học tập')
    )
    reminder_time = models.TimeField(
        default='20:00',
        verbose_name=_('Giờ nhắc nhở')
    )
    weekly_report = models.BooleanField(
        default=True,
        verbose_name=_('Báo cáo hàng tuần')
    )
    
    # Learning preferences
    sound_effects = models.BooleanField(
        default=True,
        verbose_name=_('Hiệu ứng âm thanh')
    )
    auto_play_audio = models.BooleanField(
        default=True,
        verbose_name=_('Tự động phát audio')
    )
    show_ipa = models.BooleanField(
        default=True,
        verbose_name=_('Hiển thị phiên âm IPA')
    )
    show_example = models.BooleanField(
        default=True,
        verbose_name=_('Hiển thị ví dụ')
    )
    cards_per_session = models.PositiveIntegerField(
        default=20,
        verbose_name=_('Số thẻ mỗi phiên')
    )
    
    # UI preferences
    dark_mode = models.BooleanField(
        default=False,
        verbose_name=_('Chế độ tối')
    )
    language = models.CharField(
        max_length=10,
        default='vi',
        verbose_name=_('Ngôn ngữ giao diện')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cài đặt người dùng')
        verbose_name_plural = _('Cài đặt người dùng')
    
    def __str__(self):
        return f'Settings of {self.user.email}'


class Subscription(models.Model):
    """
    User subscription for premium features.
    """
    
    class Plan(models.TextChoices):
        FREE = 'free', _('Miễn phí')
        BASIC = 'basic', _('Cơ bản')
        PREMIUM = 'premium', _('Premium')
        VIP = 'vip', _('VIP')
    
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Đang hoạt động')
        EXPIRED = 'expired', _('Đã hết hạn')
        CANCELLED = 'cancelled', _('Đã hủy')
        PAUSED = 'paused', _('Tạm dừng')
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('Người dùng')
    )
    
    plan = models.CharField(
        max_length=10,
        choices=Plan.choices,
        default=Plan.FREE,
        verbose_name=_('Gói')
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('Trạng thái')
    )
    
    starts_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Ngày bắt đầu')
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Ngày hết hạn')
    )
    
    is_auto_renew = models.BooleanField(
        default=False,
        verbose_name=_('Tự động gia hạn')
    )
    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_('Phương thức thanh toán')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Gói đăng ký')
        verbose_name_plural = _('Gói đăng ký')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.plan}'
    
    @property
    def is_active(self):
        """Check if subscription is currently active."""
        from django.utils import timezone
        if self.status != self.Status.ACTIVE:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True


class Achievement(models.Model):
    """
    Achievement/Badge definition.
    """
    
    class Category(models.TextChoices):
        STREAK = 'streak', _('Chuỗi ngày học')
        XP = 'xp', _('Điểm kinh nghiệm')
        LESSONS = 'lessons', _('Bài học')
        FLASHCARDS = 'flashcards', _('Flashcards')
        ACCURACY = 'accuracy', _('Độ chính xác')
        SPECIAL = 'special', _('Đặc biệt')
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Tên')
    )
    code = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name=_('Mã')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Mô tả')
    )
    icon = models.CharField(
        max_length=50,
        default='trophy',
        verbose_name=_('Icon')
    )
    badge_image = models.ImageField(
        upload_to='achievements/',
        null=True,
        blank=True,
        verbose_name=_('Hình huy hiệu')
    )
    
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.SPECIAL,
        verbose_name=_('Danh mục')
    )
    
    # Requirements
    requirement_type = models.CharField(
        max_length=50,
        verbose_name=_('Loại yêu cầu')
    )
    requirement_value = models.PositiveIntegerField(
        verbose_name=_('Giá trị yêu cầu')
    )
    requirement_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Cấu hình yêu cầu')
    )
    
    xp_reward = models.PositiveIntegerField(
        default=0,
        verbose_name=_('XP thưởng')
    )
    
    is_secret = models.BooleanField(
        default=False,
        verbose_name=_('Ẩn')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Kích hoạt')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Thứ tự')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Thành tựu')
        verbose_name_plural = _('Thành tựu')
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """
    User's progress towards achievements.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name=_('Người dùng')
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name=_('Thành tựu')
    )
    
    progress = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Tiến độ (%)')
    )
    current_value = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Giá trị hiện tại')
    )
    
    is_unlocked = models.BooleanField(
        default=False,
        verbose_name=_('Đã mở khóa')
    )
    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Ngày mở khóa')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Thành tựu người dùng')
        verbose_name_plural = _('Thành tựu người dùng')
        unique_together = [['user', 'achievement']]
        ordering = ['-unlocked_at', '-created_at']
    
    def __str__(self):
        status = '✓' if self.is_unlocked else f'{self.progress}%'
        return f'{self.user.email} - {self.achievement.name} ({status})'
    
    def update_progress(self, value: int) -> bool:
        """
        Update progress and check if achievement is unlocked.
        Returns True if just unlocked.
        """
        from django.utils import timezone
        
        self.current_value = value
        self.progress = min(100, int(value * 100 / self.achievement.requirement_value))
        
        if self.progress >= 100 and not self.is_unlocked:
            self.is_unlocked = True
            self.unlocked_at = timezone.now()
            self.save()
            
            # Award XP
            if self.achievement.xp_reward:
                self.user.add_xp(self.achievement.xp_reward)
            
            return True
        
        self.save()
        return False


class EmailVerification(models.Model):
    """
    Email verification codes for user registration.
    """
    email = models.EmailField(
        verbose_name=_('Email')
    )
    code = models.CharField(
        max_length=6,
        verbose_name=_('Mã xác thực')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Đã xác thực')
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Số lần thử')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        verbose_name=_('Hết hạn')
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Thời gian xác thực')
    )
    
    class Meta:
        verbose_name = _('Xác thực email')
        verbose_name_plural = _('Xác thực email')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'code']),
        ]
    
    def __str__(self):
        status = '✓' if self.is_verified else '⏳'
        return f'{self.email} - {self.code} ({status})'
    
    @classmethod
    def generate_code(cls):
        """Generate a 6-digit verification code."""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    @classmethod
    def create_verification(cls, email):
        """Create a new verification code for email."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Delete old unverified codes for this email
        cls.objects.filter(email=email.lower(), is_verified=False).delete()
        
        # Create new code
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=15)
        
        verification = cls.objects.create(
            email=email.lower(),
            code=code,
            expires_at=expires_at
        )
        return verification
    
    def is_expired(self):
        """Check if the verification code has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def verify(self, code):
        """
        Verify the code. Returns True if successful.
        """
        from django.utils import timezone
        
        self.attempts += 1
        self.save(update_fields=['attempts'])
        
        # Check attempts limit
        if self.attempts > 5:
            return False, 'Đã vượt quá số lần thử. Vui lòng yêu cầu mã mới.'
        
        # Check expiry
        if self.is_expired():
            return False, 'Mã xác thực đã hết hạn. Vui lòng yêu cầu mã mới.'
        
        # Check code
        if self.code != code:
            remaining = 5 - self.attempts
            return False, f'Mã xác thực không đúng. Còn {remaining} lần thử.'
        
        # Success
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'verified_at'])
        return True, 'Xác thực thành công!'


# =============================================================================
# PRONUNCIATION LEARNING PROGRESS MODELS
# =============================================================================

class UserPronunciationLessonProgress(models.Model):
    """
    Tracks user progress through pronunciation lessons.
    Each lesson has 5 screens: Intro, Practice 1, Practice 2, Challenge, Summary
    """
    STATUS_CHOICES = [
        ('not_started', 'Chưa bắt đầu'),
        ('in_progress', 'Đang học'),
        ('completed', 'Hoàn thành'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pronunciation_progress',
        verbose_name='Người dùng'
    )
    pronunciation_lesson = models.ForeignKey(
        'curriculum.PronunciationLesson',
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='Bài học phát âm'
    )
    
    # Progress status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        db_index=True
    )
    
    # Screen progress (1-5)
    current_screen = models.PositiveSmallIntegerField(default=1, verbose_name='Màn hình hiện tại')
    completed_screens = models.JSONField(default=list, verbose_name='Màn hình đã hoàn thành')
    
    # Screen-specific data
    # { "screen_1": {...}, "screen_2": {...}, ... }
    screen_data = models.JSONField(default=dict, blank=True, verbose_name='Dữ liệu từng màn hình')
    
    # Score and accuracy
    total_score = models.PositiveIntegerField(default=0, verbose_name='Điểm tổng')
    pronunciation_accuracy = models.FloatField(default=0.0, verbose_name='Độ chính xác phát âm (%)')
    listening_accuracy = models.FloatField(default=0.0, verbose_name='Độ chính xác nghe (%)')
    
    # Challenge results (Minimal Pairs Quiz)
    challenge_correct = models.PositiveSmallIntegerField(default=0, verbose_name='Số câu đúng')
    challenge_total = models.PositiveSmallIntegerField(default=0, verbose_name='Tổng số câu hỏi')
    
    # XP earned from this lesson
    xp_earned = models.PositiveIntegerField(default=0, verbose_name='XP nhận được')
    
    # Time tracking
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name='Thời gian học (giây)')
    
    # Completion info
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Bắt đầu lúc')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Hoàn thành lúc')
    last_accessed_at = models.DateTimeField(auto_now=True, verbose_name='Truy cập gần nhất')
    
    # Number of attempts (can restart lesson)
    attempts = models.PositiveSmallIntegerField(default=1, verbose_name='Số lần học')
    
    class Meta:
        db_table = 'user_pronunciation_lesson_progress'
        unique_together = ['user', 'pronunciation_lesson']
        ordering = ['-last_accessed_at']
        verbose_name = 'Tiến độ bài học phát âm'
        verbose_name_plural = 'Tiến độ bài học phát âm'
    
    def __str__(self):
        return f"{self.user.username} - {self.pronunciation_lesson.title} ({self.status})"
    
    def complete_screen(self, screen_number, data=None):
        """Mark a screen as completed and store its data."""
        if screen_number not in self.completed_screens:
            self.completed_screens.append(screen_number)
        
        if data:
            self.screen_data[f'screen_{screen_number}'] = data
        
        # Move to next screen
        if screen_number < 5:
            self.current_screen = screen_number + 1
        
        self.save()
    
    def calculate_xp(self):
        """Calculate XP based on performance."""
        base_xp = self.pronunciation_lesson.xp_reward
        
        # Bonus for accuracy (up to 50% bonus)
        accuracy_bonus = 0
        if self.challenge_total > 0:
            accuracy_rate = self.challenge_correct / self.challenge_total
            accuracy_bonus = int(base_xp * 0.5 * accuracy_rate)
        
        # Bonus for completing all screens
        completion_bonus = 5 if len(self.completed_screens) >= 5 else 0
        
        # First-time completion bonus
        first_time_bonus = 10 if self.attempts == 1 else 0
        
        total_xp = base_xp + accuracy_bonus + completion_bonus + first_time_bonus
        return total_xp
    
    def complete_lesson(self):
        """Mark the lesson as completed and award XP."""
        from django.utils import timezone
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.xp_earned = self.calculate_xp()
        self.save()
        
        # Add XP to user
        self.user.xp_points += self.xp_earned
        self.user.save(update_fields=['xp_points'])
        
        return self.xp_earned


class UserPhonemeProgress(models.Model):
    """
    Tracks user mastery of individual phonemes.
    Updated whenever user practices a specific sound.
    """
    MASTERY_LEVELS = [
        (0, 'Chưa học'),
        (1, 'Mới bắt đầu'),
        (2, 'Đang luyện tập'),
        (3, 'Khá tốt'),
        (4, 'Thành thạo'),
        (5, 'Hoàn hảo'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='phoneme_progress',
        verbose_name='Người dùng'
    )
    phoneme = models.ForeignKey(
        'curriculum.Phoneme',
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='Âm vị'
    )
    
    # Mastery level (0-5)
    mastery_level = models.PositiveSmallIntegerField(
        default=0,
        choices=MASTERY_LEVELS,
        verbose_name='Mức thành thạo'
    )
    
    # Practice count
    times_practiced = models.PositiveIntegerField(default=0, verbose_name='Số lần luyện tập')
    times_correct = models.PositiveIntegerField(default=0, verbose_name='Số lần đúng')
    
    # Accuracy rate (0-100)
    accuracy_rate = models.FloatField(default=0.0, verbose_name='Tỉ lệ chính xác (%)')
    
    # Last practice stats
    last_practice_accuracy = models.FloatField(default=0.0, verbose_name='Độ chính xác lần gần nhất')
    last_practiced_at = models.DateTimeField(null=True, blank=True, verbose_name='Luyện tập gần nhất')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_phoneme_progress'
        unique_together = ['user', 'phoneme']
        ordering = ['-mastery_level', '-accuracy_rate']
        verbose_name = 'Tiến độ âm vị'
        verbose_name_plural = 'Tiến độ âm vị'
    
    def __str__(self):
        return f"{self.user.username} - /{self.phoneme.ipa_symbol}/ ({self.get_mastery_level_display()})"
    
    def update_progress(self, correct_count, total_count):
        """Update progress after a practice session."""
        from django.utils import timezone
        
        self.times_practiced += total_count
        self.times_correct += correct_count
        
        # Calculate accuracy
        if self.times_practiced > 0:
            self.accuracy_rate = (self.times_correct / self.times_practiced) * 100
        
        self.last_practice_accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        self.last_practiced_at = timezone.now()
        
        # Update mastery level based on accuracy and practice count
        self._update_mastery_level()
        self.save()
    
    def _update_mastery_level(self):
        """Calculate mastery level based on accuracy and practice count."""
        if self.times_practiced == 0:
            self.mastery_level = 0
        elif self.times_practiced < 5:
            self.mastery_level = 1
        elif self.accuracy_rate < 50:
            self.mastery_level = 2
        elif self.accuracy_rate < 70:
            self.mastery_level = 3
        elif self.accuracy_rate < 90:
            self.mastery_level = 4
        else:
            self.mastery_level = 5


class UserPronunciationStreak(models.Model):
    """
    Tracks pronunciation practice streaks (separate from general study streak).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='pronunciation_streak',
        verbose_name='Người dùng'
    )
    
    current_streak = models.PositiveIntegerField(default=0, verbose_name='Chuỗi hiện tại')
    longest_streak = models.PositiveIntegerField(default=0, verbose_name='Chuỗi dài nhất')
    last_practice_date = models.DateField(null=True, blank=True, verbose_name='Ngày luyện gần nhất')
    
    # Weekly stats
    this_week_minutes = models.PositiveIntegerField(default=0, verbose_name='Phút tuần này')
    this_week_lessons = models.PositiveIntegerField(default=0, verbose_name='Bài học tuần này')
    
    # Total stats
    total_lessons_completed = models.PositiveIntegerField(default=0, verbose_name='Tổng bài học')
    total_practice_time_minutes = models.PositiveIntegerField(default=0, verbose_name='Tổng thời gian (phút)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_pronunciation_streak'
        verbose_name = 'Chuỗi luyện phát âm'
        verbose_name_plural = 'Chuỗi luyện phát âm'
    
    def __str__(self):
        return f"{self.user.username} - Streak: {self.current_streak} days"
    
    def update_streak(self, minutes_practiced=0):
        """Update streak after a practice session."""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        if self.last_practice_date is None:
            # First practice
            self.current_streak = 1
        elif self.last_practice_date == today:
            # Already practiced today, just update time
            pass
        elif self.last_practice_date == today - timedelta(days=1):
            # Practiced yesterday, extend streak
            self.current_streak += 1
        else:
            # Streak broken
            self.current_streak = 1
        
        # Update longest streak
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_practice_date = today
        self.this_week_minutes += minutes_practiced
        self.total_practice_time_minutes += minutes_practiced
        self.save()

