"""
Study models - User progress, flashcard learning, practice results.

This module contains all study-related models that track user learning progress
and implement the SRS (Spaced Repetition System) algorithm.
"""

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.curriculum.models import Course, Unit, Lesson, Sentence, Flashcard


class UserCourseEnrollment(models.Model):
    """
    Tracks user enrollment in courses.
    
    Records when a user starts a course and their overall progress.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Progress tracking
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Tiến độ (%)'
    )
    
    # Current position
    current_unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_learners'
    )
    current_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_learners'
    )
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_course_enrollments'
        unique_together = [['user', 'course']]
        verbose_name = 'Đăng ký khóa học'
        verbose_name_plural = 'Đăng ký khóa học'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    def update_progress(self):
        """Calculate and update progress percentage."""
        total_lessons = Lesson.objects.filter(unit__course=self.course).count()
        if total_lessons == 0:
            self.progress_percent = Decimal('0.00')
        else:
            completed = UserLessonProgress.objects.filter(
                user=self.user,
                lesson__unit__course=self.course,
                status='completed'
            ).count()
            self.progress_percent = Decimal(completed * 100 / total_lessons).quantize(
                Decimal('0.01')
            )
        self.save(update_fields=['progress_percent'])


class UserLessonProgress(models.Model):
    """
    Tracks individual lesson progress for each user.
    
    Records completion status, scores, and attempts for each lesson.
    """
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # Status
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='not_started',
        db_index=True
    )
    
    # Progress within the lesson (0-100)
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Scores
    best_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Điểm cao nhất (%)'
    )
    last_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Điểm gần nhất (%)'
    )
    
    # Attempts
    total_attempts = models.PositiveIntegerField(default=0)
    
    # Time tracking
    total_time_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name='Tổng thời gian học (giây)'
    )
    
    # XP earned
    xp_earned = models.PositiveIntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_lesson_progress'
        unique_together = [['user', 'lesson']]
        verbose_name = 'Tiến độ bài học'
        verbose_name_plural = 'Tiến độ bài học'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['lesson', 'status']),
            models.Index(fields=['user', 'last_accessed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}: {self.status}"
    
    def mark_completed(self, score=None):
        """Mark this lesson as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if score is not None:
            self.last_score = Decimal(str(score))
            if score > self.best_score:
                self.best_score = Decimal(str(score))
        self.total_attempts += 1
        self.save()


class UserFlashcard(models.Model):
    """
    SRS (Spaced Repetition System) tracking for flashcards.
    
    Implements the SuperMemo-2 algorithm with:
    - ease_factor: Difficulty multiplier (default 2.5)
    - box_level: Current SRS box (0-5)
    - next_review_date: When to show this card next
    """
    
    # SRS intervals in days for each box level
    SRS_INTERVALS = [0, 1, 3, 7, 14, 30, 60]  # Box 0-6
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flashcard_progress'
    )
    flashcard = models.ForeignKey(
        Flashcard,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # SRS fields
    box_level = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='SRS Box Level (0-6)'
    )
    ease_factor = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('2.50'),
        verbose_name='Ease Factor'
    )
    next_review_date = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name='Ngày ôn tập tiếp theo'
    )
    
    # Review statistics
    review_count = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    incorrect_count = models.PositiveIntegerField(default=0)
    
    # Streak tracking
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    
    # Mastery status
    is_mastered = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Đã thành thạo'
    )
    mastered_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_flashcards'
        unique_together = [['user', 'flashcard']]
        verbose_name = 'User Flashcard'
        verbose_name_plural = 'User Flashcards'
        indexes = [
            models.Index(fields=['user', 'next_review_date']),
            models.Index(fields=['user', 'is_mastered']),
            models.Index(fields=['user', 'box_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.flashcard.front_text[:30]}..."
    
    @property
    def accuracy_rate(self):
        """Calculate accuracy rate as percentage."""
        if self.review_count == 0:
            return Decimal('0.00')
        return Decimal(self.correct_count * 100 / self.review_count).quantize(
            Decimal('0.01')
        )
    
    def process_review(self, quality: int):
        """
        Process a review response using SuperMemo-2 algorithm.
        
        Args:
            quality: Response quality (0-5)
                0: Complete blackout
                1: Incorrect, but recognized
                2: Incorrect, but easy to recall
                3: Correct, with difficulty
                4: Correct, with hesitation
                5: Perfect response
        """
        self.review_count += 1
        self.last_reviewed_at = timezone.now()
        
        if quality >= 3:
            # Correct response
            self.correct_count += 1
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            
            # Move to next box (max 6)
            if self.box_level < 6:
                self.box_level += 1
            
            # Update ease factor
            self.ease_factor = max(
                Decimal('1.30'),
                self.ease_factor + Decimal('0.1') - Decimal(str((5 - quality) * (0.08 + (5 - quality) * 0.02)))
            )
        else:
            # Incorrect response
            self.incorrect_count += 1
            self.current_streak = 0
            
            # Reset to box 0 or 1
            self.box_level = 0 if quality <= 1 else 1
            
            # Decrease ease factor
            self.ease_factor = max(
                Decimal('1.30'),
                self.ease_factor - Decimal('0.20')
            )
        
        # Calculate next review date
        interval = self.SRS_INTERVALS[min(self.box_level, 6)]
        adjusted_interval = int(interval * float(self.ease_factor))
        self.next_review_date = timezone.now() + timedelta(days=adjusted_interval)
        
        # Check mastery (box level 5+ with 90%+ accuracy)
        if self.box_level >= 5 and self.accuracy_rate >= Decimal('90.00'):
            if not self.is_mastered:
                self.is_mastered = True
                self.mastered_at = timezone.now()
        
        self.save()


class UserSentenceProgress(models.Model):
    """
    Tracks user progress on individual sentences.
    
    Used for dictation and listening practice.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sentence_progress'
    )
    sentence = models.ForeignKey(
        Sentence,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # Practice counts
    dictation_attempts = models.PositiveIntegerField(default=0)
    dictation_correct = models.PositiveIntegerField(default=0)
    listening_attempts = models.PositiveIntegerField(default=0)
    listening_correct = models.PositiveIntegerField(default=0)
    speaking_attempts = models.PositiveIntegerField(default=0)
    
    # Best scores (percentage)
    best_dictation_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    best_speaking_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Mastery
    is_mastered = models.BooleanField(default=False, db_index=True)
    
    # Timestamps
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_practiced_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sentence_progress'
        unique_together = [['user', 'sentence']]
        verbose_name = 'User Sentence Progress'
        verbose_name_plural = 'User Sentence Progress'
        indexes = [
            models.Index(fields=['user', 'is_mastered']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Sentence #{self.sentence_id}"


class PracticeSession(models.Model):
    """
    Tracks individual practice sessions.
    
    Records metadata about each practice session for analytics.
    """
    
    SESSION_TYPE_CHOICES = [
        ('flashcard', 'Flashcard Review'),
        ('dictation', 'Dictation'),
        ('listening', 'Listening'),
        ('speaking', 'Speaking'),
        ('grammar', 'Grammar'),
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('test', 'Practice Test'),
        ('mixed', 'Mixed Practice'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practice_sessions'
    )
    
    # Session info
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        db_index=True
    )
    
    # Related content (optional)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='practice_sessions'
    )
    
    # Session metrics
    total_items = models.PositiveIntegerField(default=0)
    correct_items = models.PositiveIntegerField(default=0)
    incorrect_items = models.PositiveIntegerField(default=0)
    skipped_items = models.PositiveIntegerField(default=0)
    
    # Score
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Time tracking
    duration_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name='Thời gian (giây)'
    )
    
    # XP earned
    xp_earned = models.PositiveIntegerField(default=0)
    
    # Session details - JSON for flexible storage
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Chi tiết phiên'
    )
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'practice_sessions'
        ordering = ['-started_at']
        verbose_name = 'Phiên luyện tập'
        verbose_name_plural = 'Phiên luyện tập'
        indexes = [
            models.Index(fields=['user', 'session_type']),
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['session_type', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.session_type} - {self.started_at}"
    
    @property
    def accuracy_rate(self):
        """Calculate accuracy rate."""
        answered = self.correct_items + self.incorrect_items
        if answered == 0:
            return Decimal('0.00')
        return Decimal(self.correct_items * 100 / answered).quantize(Decimal('0.01'))


class PracticeResult(models.Model):
    """
    Individual practice item results within a session.
    
    Tracks each question/item answered during practice.
    """
    
    RESULT_CHOICES = [
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
        ('partial', 'Partially Correct'),
        ('skipped', 'Skipped'),
    ]
    
    session = models.ForeignKey(
        PracticeSession,
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    # Content reference (one of these will be set)
    flashcard = models.ForeignKey(
        Flashcard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='practice_results'
    )
    sentence = models.ForeignKey(
        Sentence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='practice_results'
    )
    
    # Result
    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES,
        db_index=True
    )
    
    # User's answer
    user_answer = models.TextField(blank=True)
    correct_answer = models.TextField(blank=True)
    
    # Score for this item (0-100)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Response time in milliseconds
    response_time_ms = models.PositiveIntegerField(
        default=0,
        verbose_name='Thời gian phản hồi (ms)'
    )
    
    # Quality rating for SRS (0-5)
    quality_rating = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Quality Rating (SRS)'
    )
    
    # Order in session
    order = models.PositiveIntegerField(default=0)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'practice_results'
        ordering = ['session', 'order']
        verbose_name = 'Kết quả luyện tập'
        verbose_name_plural = 'Kết quả luyện tập'
        indexes = [
            models.Index(fields=['session', 'result']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - Item {self.order}: {self.result}"


class DailyStreak(models.Model):
    """
    Tracks daily study streaks for gamification.
    
    Records each day the user studied to calculate streaks.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_streaks'
    )
    
    # Date of study (no time component)
    study_date = models.DateField(db_index=True)
    
    # Metrics for the day
    minutes_studied = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    flashcards_reviewed = models.PositiveIntegerField(default=0)
    
    # Goals met
    daily_goal_met = models.BooleanField(default=False)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_streaks'
        unique_together = [['user', 'study_date']]
        ordering = ['-study_date']
        verbose_name = 'Daily Study Record'
        verbose_name_plural = 'Daily Study Records'
        indexes = [
            models.Index(fields=['user', 'study_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.study_date}"


class LearningGoal(models.Model):
    """
    User's learning goals for motivation tracking.
    """
    
    GOAL_TYPE_CHOICES = [
        ('daily_xp', 'Daily XP'),
        ('daily_minutes', 'Daily Minutes'),
        ('weekly_lessons', 'Weekly Lessons'),
        ('monthly_flashcards', 'Monthly Flashcards'),
        ('course_completion', 'Course Completion'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_goals'
    )
    
    # Goal definition
    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPE_CHOICES,
        db_index=True
    )
    period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        default='daily'
    )
    target_value = models.PositiveIntegerField(verbose_name='Mục tiêu')
    current_value = models.PositiveIntegerField(default=0, verbose_name='Hiện tại')
    
    # Related course (optional)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_goals'
    )
    
    # Active flag
    is_active = models.BooleanField(default=True)
    
    # Period dates
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_goals'
        ordering = ['-created_at']
        verbose_name = 'Mục tiêu học tập'
        verbose_name_plural = 'Mục tiêu học tập'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'goal_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.goal_type}: {self.target_value}"
    
    @property
    def progress_percent(self):
        """Calculate progress percentage."""
        if self.target_value == 0:
            return Decimal('0.00')
        percent = min(100, self.current_value * 100 / self.target_value)
        return Decimal(str(percent)).quantize(Decimal('0.01'))
    
    def check_completion(self):
        """Check and update completion status."""
        if self.current_value >= self.target_value and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])
            return True
        return False


# ============================================
# DISCRIMINATION PRACTICE MODELS (Days 6-7)
# ============================================

class DiscriminationSession(models.Model):
    """
    Groups multiple discrimination attempts into a quiz session.
    Tracks session-level statistics and timing.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
    ]
    
    # Foreign Keys
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discrimination_sessions',
        verbose_name='Người dùng'
    )
    
    # Session details
    session_id = models.CharField(
        max_length=36,
        unique=True,
        help_text='UUID for this session',
        verbose_name='ID phiên',
        db_index=True
    )
    total_questions = models.PositiveSmallIntegerField(
        default=10,
        verbose_name='Tổng số câu'
    )
    correct_answers = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Số câu đúng'
    )
    accuracy = models.FloatField(
        default=0.0,
        help_text='Percentage: 0-100',
        verbose_name='Độ chính xác (%)'
    )
    
    # Time tracking
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Bắt đầu'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Hoàn thành'
    )
    time_limit_seconds = models.PositiveIntegerField(
        default=300,  # 5 minutes
        verbose_name='Giới hạn thời gian (giây)'
    )
    time_spent_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name='Thời gian đã dùng (giây)'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        db_index=True,
        verbose_name='Trạng thái'
    )
    
    class Meta:
        db_table = 'discrimination_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
        verbose_name = 'Phiên phân biệt âm'
        verbose_name_plural = 'Phiên phân biệt âm'
    
    def __str__(self):
        return f"{self.user.username} - {self.accuracy:.1f}% ({self.status})"
    
    def calculate_accuracy(self):
        """Calculate and update accuracy based on attempts."""
        if self.total_questions > 0:
            self.accuracy = (self.correct_answers / self.total_questions) * 100
            self.save(update_fields=['accuracy'])
    
    def complete_session(self):
        """Mark session as completed and calculate final stats."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.started_at:
            time_diff = self.completed_at - self.started_at
            self.time_spent_seconds = int(time_diff.total_seconds())
        self.calculate_accuracy()
        self.save(update_fields=['status', 'completed_at', 'time_spent_seconds', 'accuracy'])


class DiscriminationAttempt(models.Model):
    """
    Records user's answer to a single discrimination question.
    Each question presents two words with different phonemes.
    """
    QUESTION_TYPE_CHOICES = [
        ('which_word', 'Which word did you hear?'),
        ('same_different', 'Are these the same or different?'),
    ]
    
    ANSWER_CHOICES = [
        ('word_1', 'Word 1'),
        ('word_2', 'Word 2'),
    ]
    
    # Foreign Keys
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discrimination_attempts',
        verbose_name='Người dùng'
    )
    session = models.ForeignKey(
        DiscriminationSession,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Phiên'
    )
    minimal_pair = models.ForeignKey(
        'curriculum.MinimalPair',
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Cặp tối thiểu'
    )
    
    # Question details
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='which_word',
        verbose_name='Loại câu hỏi'
    )
    question_number = models.PositiveSmallIntegerField(
        help_text='Question number within session (1-10)',
        verbose_name='Số câu hỏi'
    )
    
    # Answer tracking
    correct_word = models.CharField(
        max_length=10,
        choices=ANSWER_CHOICES,
        verbose_name='Từ đúng'
    )
    user_answer = models.CharField(
        max_length=10,
        choices=ANSWER_CHOICES,
        verbose_name='Câu trả lời'
    )
    
    # Results
    is_correct = models.BooleanField(
        verbose_name='Đúng'
    )
    response_time = models.FloatField(
        help_text='Time taken to answer in seconds',
        verbose_name='Thời gian phản hồi (giây)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    
    class Meta:
        db_table = 'discrimination_attempts'
        ordering = ['session', 'question_number']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session', 'question_number']),
        ]
        verbose_name = 'Lần thử phân biệt âm'
        verbose_name_plural = 'Lần thử phân biệt âm'
    
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{self.user.username} - Q{self.question_number} [{status}]"


# ============================================
# PRODUCTION PRACTICE MODELS (Days 8-9)
# ============================================

class ProductionRecording(models.Model):
    """
    Stores audio recording of user's pronunciation attempt.
    Includes self-assessment and future AI scoring capability.
    """
    RATING_CHOICES = [
        (1, '1 Star - Need more practice'),
        (2, '2 Stars - Getting better'),
        (3, '3 Stars - Good attempt'),
        (4, '4 Stars - Very good'),
        (5, '5 Stars - Native-like'),
    ]
    
    # Foreign Keys
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='production_recordings',
        verbose_name='Người dùng'
    )
    phoneme = models.ForeignKey(
        'curriculum.Phoneme',
        on_delete=models.CASCADE,
        related_name='user_recordings',
        verbose_name='Âm vị'
    )
    
    # Recording file
    recording_file = models.FileField(
        upload_to='user_recordings/%Y/%m/%d/',
        help_text='Audio file (WebM, MP4, etc.)',
        verbose_name='File ghi âm'
    )
    duration_seconds = models.FloatField(
        help_text='Recording duration in seconds',
        verbose_name='Thời lượng (giây)'
    )
    file_size_bytes = models.PositiveIntegerField(
        default=0,
        verbose_name='Kích thước file (bytes)'
    )
    mime_type = models.CharField(
        max_length=50,
        default='audio/webm',
        verbose_name='Loại MIME'
    )
    
    # Scoring
    self_assessment_score = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text='User self-rating (1-5 stars)',
        verbose_name='Tự đánh giá (1-5 sao)'
    )
    ai_score = models.FloatField(
        null=True,
        blank=True,
        help_text='AI pronunciation analysis score (0-100). Future feature.',
        verbose_name='Điểm AI (0-100)'
    )
    ai_feedback = models.TextField(
        blank=True,
        help_text='AI-generated pronunciation feedback. Future feature.',
        verbose_name='Phản hồi từ AI'
    )
    
    # Metadata
    is_best = models.BooleanField(
        default=False,
        help_text='Mark as user\'s best recording for this phoneme',
        verbose_name='Ghi âm tốt nhất',
        db_index=True
    )
    notes = models.TextField(
        blank=True,
        help_text='User notes about this recording',
        verbose_name='Ghi chú'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    
    class Meta:
        db_table = 'production_recordings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'phoneme', '-created_at']),
            models.Index(fields=['user', 'is_best']),
        ]
        verbose_name = 'Ghi âm phát âm'
        verbose_name_plural = 'Ghi âm phát âm'
    
    def __str__(self):
        stars = '⭐' * (self.self_assessment_score or 0)
        return f"{self.user.username} - {self.phoneme.ipa_symbol} {stars}"
    
    def save(self, *args, **kwargs):
        """Auto-unmark previous 'is_best' if this is marked as best."""
        if self.is_best:
            ProductionRecording.objects.filter(
                user=self.user,
                phoneme=self.phoneme,
                is_best=True
            ).exclude(pk=self.pk).update(is_best=False)
        super().save(*args, **kwargs)
