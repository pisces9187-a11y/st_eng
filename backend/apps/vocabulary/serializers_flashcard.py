"""
Serializers for Flashcard Study API.
"""

from rest_framework import serializers
from .models import (
    Word, Flashcard, FlashcardDeck, UserFlashcardProgress, StudySession
)
from .models_achievement import Achievement, UserAchievement
from services.tts_flashcard_service import get_tts_service


class WordSerializer(serializers.ModelSerializer):
    """Serializer for Word model."""
    
    # NEW: Audio URLs
    audio_url = serializers.SerializerMethodField()
    audio_urls = serializers.SerializerMethodField()
    
    class Meta:
        model = Word
        fields = [
            'id', 'text', 'pos', 'cefr_level',
            'ipa', 'british_ipa', 'american_ipa',
            'meaning_vi', 'meaning_en',
            'example_en', 'example_vi',
            'collocations', 'synonyms', 'antonyms',
            'audio_url', 'audio_urls'  # NEW
        ]
    
    def get_audio_url(self, obj):
        """Get default audio URL (US male, normal speed)."""
        tts_service = get_tts_service()
        return tts_service.get_audio_url(obj.text, voice='us_male', speed='normal')
    
    def get_audio_urls(self, obj):
        """Get all available audio URLs for this word."""
        tts_service = get_tts_service()
        
        urls = {}
        for voice_id in ['us_male', 'us_female', 'uk_male', 'uk_female']:
            voice_code = tts_service.VOICES[voice_id]
            for speed in ['slow', 'normal', 'fast']:
                url = tts_service.get_audio_url(obj.text, voice_code, speed)
                if url:
                    key = f"{voice_id}_{speed}"
                    urls[key] = url
        
        return urls if urls else None


class FlashcardStudySerializer(serializers.ModelSerializer):
    """
    Serializer for flashcard in study session.
    Includes word details and user progress.
    """
    
    word = WordSerializer(read_only=True)
    last_reviewed = serializers.SerializerMethodField()
    times_reviewed = serializers.SerializerMethodField()
    mastery_level = serializers.SerializerMethodField()
    
    # NEW: Quick audio access
    audio_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Flashcard
        fields = [
            'id', 'word', 'front_text', 'back_text',
            'difficulty', 'hint', 'audio_url',  # NEW
            'last_reviewed', 'times_reviewed', 'mastery_level'
        ]
    
    def get_audio_url(self, obj):
        """Get default audio URL for flashcard word."""
        if obj.word:
            tts_service = get_tts_service()
            return tts_service.get_audio_url(obj.word.text)
        return None
    
    def get_last_reviewed(self, obj):
        """Get last review date for current user."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            progress = UserFlashcardProgress.objects.get(
                user=request.user,
                flashcard=obj
            )
            return progress.last_reviewed_at
        except UserFlashcardProgress.DoesNotExist:
            return None
    
    def get_times_reviewed(self, obj):
        """Get number of times reviewed by current user."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        try:
            progress = UserFlashcardProgress.objects.get(
                user=request.user,
                flashcard=obj
            )
            return progress.total_reviews
        except UserFlashcardProgress.DoesNotExist:
            return 0
    
    def get_mastery_level(self, obj):
        """Get mastery level: new, learning, mastered."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 'new'
        
        try:
            progress = UserFlashcardProgress.objects.get(
                user=request.user,
                flashcard=obj
            )
            if progress.is_mastered:
                return 'mastered'
            elif progress.total_reviews > 0:
                return 'learning'
            else:
                return 'new'
        except UserFlashcardProgress.DoesNotExist:
            return 'new'


class FlashcardDeckSerializer(serializers.ModelSerializer):
    """Serializer for flashcard deck."""
    
    card_count = serializers.IntegerField(read_only=True)
    mastered_count = serializers.SerializerMethodField()
    new_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = FlashcardDeck
        fields = [
            'id', 'name', 'description', 'category', 'level',
            'icon', 'color', 'is_public', 'is_official',
            'card_count', 'mastered_count', 'new_count', 'review_count',
            'progress_percentage'
        ]
    
    def get_mastered_count(self, obj):
        """Count mastered cards for current user."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        return UserFlashcardProgress.objects.filter(
            user=request.user,
            flashcard__deck=obj,
            is_mastered=True
        ).count()
    
    def get_new_count(self, obj):
        """Count new cards (not yet studied)."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return obj.card_count
        
        studied_ids = UserFlashcardProgress.objects.filter(
            user=request.user,
            flashcard__deck=obj
        ).values_list('flashcard_id', flat=True)
        
        return obj.flashcards.exclude(id__in=studied_ids).count()
    
    def get_review_count(self, obj):
        """Count cards due for review."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        from django.utils import timezone
        return UserFlashcardProgress.objects.filter(
            user=request.user,
            flashcard__deck=obj,
            next_review_date__lte=timezone.now(),
            is_learning=True
        ).count()
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage."""
        mastered = self.get_mastered_count(obj)
        total = obj.card_count
        
        if total == 0:
            return 0
        
        return int((mastered / total) * 100)


class StudySessionSerializer(serializers.ModelSerializer):
    """Serializer for study session."""
    
    deck_name = serializers.CharField(source='deck.name', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = StudySession
        fields = [
            'id', 'deck', 'deck_name',
            'started_at', 'ended_at',
            'cards_studied', 'cards_correct', 'cards_incorrect',
            'accuracy', 'time_spent_seconds', 'duration_minutes',
            'average_time_per_card',
            'streak_count', 'is_goal_reached'
        ]
        read_only_fields = ['started_at']
    
    def get_duration_minutes(self, obj):
        """Get duration in minutes."""
        if obj.time_spent_seconds:
            return round(obj.time_spent_seconds / 60, 1)
        return 0


class ReviewCardRequestSerializer(serializers.Serializer):
    """Serializer for card review request."""
    
    quality = serializers.IntegerField(min_value=0, max_value=5)
    time_spent = serializers.IntegerField(min_value=0, required=False, default=0)


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievement."""
    
    progress = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    unlocked_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'key', 'name', 'description', 'icon', 'category',
            'requirement_type', 'requirement_value',
            'points', 'progress', 'is_unlocked', 'unlocked_at'
        ]
    
    def get_progress(self, obj):
        """Get user's progress toward this achievement."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        # This is a simplified version - you'd calculate actual progress
        # based on requirement_type
        return 0
    
    def get_is_unlocked(self, obj):
        """Check if user has unlocked this achievement."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        return UserAchievement.objects.filter(
            user=request.user,
            achievement=obj
        ).exists()
    
    def get_unlocked_at(self, obj):
        """Get unlock date if unlocked."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            user_achievement = UserAchievement.objects.get(
                user=request.user,
                achievement=obj
            )
            return user_achievement.unlocked_at
        except UserAchievement.DoesNotExist:
            return None


class DailyProgressSerializer(serializers.Serializer):
    """Serializer for daily progress data."""
    
    cards_learned = serializers.IntegerField()
    goal = serializers.IntegerField()
    percentage = serializers.IntegerField()
    time_spent_minutes = serializers.IntegerField()
    goal_reached = serializers.BooleanField()


class StreakSerializer(serializers.Serializer):
    """Serializer for streak data."""
    
    current = serializers.IntegerField()
    longest = serializers.IntegerField()
    updated = serializers.BooleanField(required=False)
    increased = serializers.BooleanField(required=False)
    broken = serializers.BooleanField(required=False)
