"""
Admin configuration for Study app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    UserCourseEnrollment, UserLessonProgress, UserFlashcard,
    UserSentenceProgress, PracticeSession, PracticeResult,
    DailyStreak, LearningGoal
)


@admin.register(UserCourseEnrollment)
class UserCourseEnrollmentAdmin(admin.ModelAdmin):
    """Admin for UserCourseEnrollment."""
    
    list_display = [
        'user', 'course', 'status', 'progress_display',
        'enrolled_at', 'last_activity_at'
    ]
    list_filter = ['status', 'course__cefr_level', 'enrolled_at']
    search_fields = ['user__username', 'user__email', 'course__title']
    raw_id_fields = ['user', 'course', 'current_unit', 'current_lesson']
    date_hierarchy = 'enrolled_at'
    ordering = ['-enrolled_at']
    
    def progress_display(self, obj):
        percent = float(obj.progress_percent)
        color = 'green' if percent >= 80 else 'orange' if percent >= 40 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percent
        )
    progress_display.short_description = 'Progress'


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    """Admin for UserLessonProgress."""
    
    list_display = [
        'user', 'lesson', 'status', 'best_score', 
        'total_attempts', 'xp_earned', 'last_accessed_at'
    ]
    list_filter = ['status', 'lesson__lesson_type', 'last_accessed_at']
    search_fields = ['user__username', 'lesson__title']
    raw_id_fields = ['user', 'lesson']
    date_hierarchy = 'last_accessed_at'
    ordering = ['-last_accessed_at']
    
    readonly_fields = [
        'total_time_seconds', 'xp_earned', 'total_attempts',
        'started_at', 'completed_at', 'last_accessed_at'
    ]


@admin.register(UserFlashcard)
class UserFlashcardAdmin(admin.ModelAdmin):
    """Admin for UserFlashcard (SRS tracking)."""
    
    list_display = [
        'user', 'flashcard_preview', 'box_level', 'ease_factor',
        'next_review_date', 'accuracy_display', 'is_mastered'
    ]
    list_filter = ['box_level', 'is_mastered', 'next_review_date']
    search_fields = ['user__username', 'flashcard__front_text']
    raw_id_fields = ['user', 'flashcard']
    date_hierarchy = 'next_review_date'
    ordering = ['next_review_date']
    
    readonly_fields = [
        'review_count', 'correct_count', 'incorrect_count',
        'current_streak', 'longest_streak', 'first_seen_at',
        'last_reviewed_at', 'mastered_at'
    ]
    
    def flashcard_preview(self, obj):
        text = obj.flashcard.front_text[:30]
        if len(obj.flashcard.front_text) > 30:
            text += '...'
        return text
    flashcard_preview.short_description = 'Flashcard'
    
    def accuracy_display(self, obj):
        rate = obj.accuracy_rate
        color = 'green' if rate >= 80 else 'orange' if rate >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, float(rate)
        )
    accuracy_display.short_description = 'Accuracy'


@admin.register(UserSentenceProgress)
class UserSentenceProgressAdmin(admin.ModelAdmin):
    """Admin for UserSentenceProgress."""
    
    list_display = [
        'user', 'sentence_id', 'dictation_attempts', 
        'best_dictation_score', 'is_mastered', 'last_practiced_at'
    ]
    list_filter = ['is_mastered', 'last_practiced_at']
    search_fields = ['user__username', 'sentence__text_content']
    raw_id_fields = ['user', 'sentence']
    ordering = ['-last_practiced_at']


class PracticeResultInline(admin.TabularInline):
    """Inline for PracticeResult in PracticeSession admin."""
    model = PracticeResult
    extra = 0
    fields = ['order', 'result', 'score', 'response_time_ms']
    readonly_fields = ['order', 'result', 'score', 'response_time_ms']
    show_change_link = True
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    """Admin for PracticeSession."""
    
    list_display = [
        'user', 'session_type', 'total_items', 'score',
        'accuracy_display', 'duration_display', 'xp_earned', 'started_at'
    ]
    list_filter = ['session_type', 'started_at']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user', 'lesson']
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    
    readonly_fields = [
        'total_items', 'correct_items', 'incorrect_items', 'skipped_items',
        'score', 'duration_seconds', 'xp_earned', 'started_at', 'completed_at'
    ]
    
    inlines = [PracticeResultInline]
    
    def accuracy_display(self, obj):
        rate = obj.accuracy_rate
        color = 'green' if rate >= 80 else 'orange' if rate >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, float(rate)
        )
    accuracy_display.short_description = 'Accuracy'
    
    def duration_display(self, obj):
        minutes = obj.duration_seconds // 60
        seconds = obj.duration_seconds % 60
        return f"{minutes}m {seconds}s"
    duration_display.short_description = 'Duration'


@admin.register(PracticeResult)
class PracticeResultAdmin(admin.ModelAdmin):
    """Admin for PracticeResult."""
    
    list_display = [
        'session', 'order', 'result', 'score', 
        'response_time_ms', 'quality_rating', 'created_at'
    ]
    list_filter = ['result', 'created_at']
    search_fields = ['session__user__username']
    raw_id_fields = ['session', 'flashcard', 'sentence']
    ordering = ['-created_at', 'order']
    
    readonly_fields = [
        'session', 'flashcard', 'sentence', 'result',
        'user_answer', 'correct_answer', 'score',
        'response_time_ms', 'quality_rating', 'order', 'created_at'
    ]


@admin.register(DailyStreak)
class DailyStreakAdmin(admin.ModelAdmin):
    """Admin for DailyStreak."""
    
    list_display = [
        'user', 'study_date', 'minutes_studied', 'xp_earned',
        'lessons_completed', 'flashcards_reviewed', 'daily_goal_met'
    ]
    list_filter = ['daily_goal_met', 'study_date']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'study_date'
    ordering = ['-study_date']
    
    readonly_fields = [
        'minutes_studied', 'xp_earned', 'lessons_completed',
        'flashcards_reviewed', 'created_at'
    ]


@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    """Admin for LearningGoal."""
    
    list_display = [
        'user', 'goal_type', 'period', 'progress_display',
        'is_active', 'is_completed', 'period_start', 'period_end'
    ]
    list_filter = ['goal_type', 'period', 'is_active', 'is_completed']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user', 'course']
    ordering = ['-created_at']
    
    def progress_display(self, obj):
        percent = float(obj.progress_percent)
        color = 'green' if percent >= 100 else 'orange' if percent >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} ({:.0f}%)</span>',
            color, obj.current_value, obj.target_value, percent
        )
    progress_display.short_description = 'Progress'
