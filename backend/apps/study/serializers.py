"""
Serializers for Study app.

Handles serialization for progress tracking, SRS flashcards,
practice sessions, and learning goals.
"""

from rest_framework import serializers

from apps.curriculum.serializers import (
    CourseListSerializer, LessonListSerializer,
    FlashcardMinimalSerializer, SentenceMinimalSerializer
)
from .models import (
    UserCourseEnrollment, UserLessonProgress, UserFlashcard,
    UserSentenceProgress, PracticeSession, PracticeResult,
    DailyStreak, LearningGoal
)


class UserCourseEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for UserCourseEnrollment."""
    
    course = CourseListSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = UserCourseEnrollment
        fields = [
            'id', 'course', 'status', 'status_display',
            'progress_percent', 'current_unit', 'current_lesson',
            'enrolled_at', 'started_at', 'completed_at', 'last_activity_at'
        ]
        read_only_fields = [
            'id', 'progress_percent', 'enrolled_at',
            'started_at', 'completed_at', 'last_activity_at'
        ]


class UserCourseEnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating course enrollment."""
    
    class Meta:
        model = UserCourseEnrollment
        fields = ['course']
    
    def validate_course(self, value):
        user = self.context['request'].user
        if UserCourseEnrollment.objects.filter(user=user, course=value).exists():
            raise serializers.ValidationError('Bạn đã đăng ký khóa học này.')
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserLessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserLessonProgress."""
    
    lesson = LessonListSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = UserLessonProgress
        fields = [
            'id', 'lesson', 'status', 'status_display',
            'progress_percent', 'best_score', 'last_score',
            'total_attempts', 'total_time_seconds', 'xp_earned',
            'started_at', 'completed_at', 'last_accessed_at'
        ]
        read_only_fields = fields


class UserLessonProgressUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating lesson progress."""
    
    class Meta:
        model = UserLessonProgress
        fields = ['status', 'progress_percent', 'last_score']


class UserFlashcardSerializer(serializers.ModelSerializer):
    """Serializer for UserFlashcard (SRS data)."""
    
    flashcard = FlashcardMinimalSerializer(read_only=True)
    accuracy_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = UserFlashcard
        fields = [
            'id', 'flashcard', 'box_level', 'ease_factor',
            'next_review_date', 'review_count',
            'correct_count', 'incorrect_count',
            'current_streak', 'longest_streak',
            'is_mastered', 'accuracy_rate',
            'first_seen_at', 'last_reviewed_at'
        ]
        read_only_fields = fields


class FlashcardReviewSerializer(serializers.Serializer):
    """Serializer for submitting flashcard review."""
    
    flashcard_id = serializers.IntegerField()
    quality = serializers.IntegerField(min_value=0, max_value=5)
    response_time_ms = serializers.IntegerField(min_value=0, required=False)
    
    def validate_flashcard_id(self, value):
        from apps.curriculum.models import Flashcard
        if not Flashcard.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Flashcard không tồn tại.')
        return value


class FlashcardReviewBatchSerializer(serializers.Serializer):
    """Serializer for batch flashcard review."""
    
    reviews = FlashcardReviewSerializer(many=True)


class UserSentenceProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserSentenceProgress."""
    
    sentence = SentenceMinimalSerializer(read_only=True)
    
    class Meta:
        model = UserSentenceProgress
        fields = [
            'id', 'sentence',
            'dictation_attempts', 'dictation_correct',
            'listening_attempts', 'listening_correct',
            'speaking_attempts',
            'best_dictation_score', 'best_speaking_score',
            'is_mastered', 'first_seen_at', 'last_practiced_at'
        ]
        read_only_fields = fields


class PracticeResultSerializer(serializers.ModelSerializer):
    """Serializer for PracticeResult."""
    
    result_display = serializers.CharField(
        source='get_result_display',
        read_only=True
    )
    
    class Meta:
        model = PracticeResult
        fields = [
            'id', 'flashcard', 'sentence',
            'result', 'result_display',
            'user_answer', 'correct_answer',
            'score', 'response_time_ms', 'quality_rating',
            'order', 'created_at'
        ]
        read_only_fields = fields


class PracticeSessionSerializer(serializers.ModelSerializer):
    """Serializer for PracticeSession."""
    
    results = PracticeResultSerializer(many=True, read_only=True)
    session_type_display = serializers.CharField(
        source='get_session_type_display',
        read_only=True
    )
    accuracy_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    lesson_title = serializers.CharField(
        source='lesson.title',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = PracticeSession
        fields = [
            'id', 'session_type', 'session_type_display',
            'lesson', 'lesson_title',
            'total_items', 'correct_items', 'incorrect_items', 'skipped_items',
            'score', 'accuracy_rate', 'duration_seconds', 'xp_earned',
            'details', 'started_at', 'completed_at',
            'results'
        ]
        read_only_fields = fields


class PracticeSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating practice session."""
    
    class Meta:
        model = PracticeSession
        fields = ['session_type', 'lesson']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PracticeSessionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating/completing practice session."""
    
    class Meta:
        model = PracticeSession
        fields = [
            'total_items', 'correct_items', 'incorrect_items', 'skipped_items',
            'score', 'duration_seconds', 'details', 'completed_at'
        ]


class PracticeResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating practice result."""
    
    class Meta:
        model = PracticeResult
        fields = [
            'session', 'flashcard', 'sentence',
            'result', 'user_answer', 'correct_answer',
            'score', 'response_time_ms', 'quality_rating', 'order'
        ]
    
    def validate(self, attrs):
        if not attrs.get('flashcard') and not attrs.get('sentence'):
            raise serializers.ValidationError(
                'Phải có flashcard hoặc sentence.'
            )
        return attrs


class DailyStreakSerializer(serializers.ModelSerializer):
    """Serializer for DailyStreak."""
    
    class Meta:
        model = DailyStreak
        fields = [
            'id', 'study_date', 'minutes_studied', 'xp_earned',
            'lessons_completed', 'flashcards_reviewed', 'daily_goal_met'
        ]
        read_only_fields = fields


class LearningGoalSerializer(serializers.ModelSerializer):
    """Serializer for LearningGoal."""
    
    goal_type_display = serializers.CharField(
        source='get_goal_type_display',
        read_only=True
    )
    period_display = serializers.CharField(
        source='get_period_display',
        read_only=True
    )
    progress_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = LearningGoal
        fields = [
            'id', 'goal_type', 'goal_type_display',
            'period', 'period_display',
            'target_value', 'current_value', 'progress_percent',
            'course', 'is_active', 'is_completed',
            'period_start', 'period_end', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_value', 'is_completed',
            'completed_at', 'created_at', 'updated_at'
        ]


class LearningGoalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating learning goal."""
    
    class Meta:
        model = LearningGoal
        fields = [
            'goal_type', 'period', 'target_value',
            'course', 'period_start', 'period_end'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StudyStatsSerializer(serializers.Serializer):
    """Serializer for overall study statistics."""
    
    total_xp = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    total_lessons_completed = serializers.IntegerField()
    total_flashcards_mastered = serializers.IntegerField()
    total_study_time_minutes = serializers.IntegerField()
    courses_enrolled = serializers.IntegerField()
    courses_completed = serializers.IntegerField()
    current_level = serializers.CharField()
    achievements_unlocked = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard data."""
    
    stats = StudyStatsSerializer()
    recent_activity = PracticeSessionSerializer(many=True)
    due_flashcards_count = serializers.IntegerField()
    active_goals = LearningGoalSerializer(many=True)
    streak_calendar = DailyStreakSerializer(many=True)
    current_courses = UserCourseEnrollmentSerializer(many=True)
