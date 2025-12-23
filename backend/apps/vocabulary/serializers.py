"""
Vocabulary API Serializers

Converts models to JSON for REST API endpoints.
"""

from rest_framework import serializers
from .models import Word, FlashcardDeck, Flashcard, UserFlashcardProgress, StudySession


class WordSerializer(serializers.ModelSerializer):
    """Basic word serializer for list views"""
    
    class Meta:
        model = Word
        fields = [
            'id', 'text', 'pos', 'cefr_level', 
            'meaning_vi', 'ipa', 'frequency_rank'
        ]


class WordDetailSerializer(serializers.ModelSerializer):
    """Detailed word serializer with all fields"""
    
    difficulty = serializers.ReadOnlyField(source='difficulty_score')
    
    class Meta:
        model = Word
        fields = '__all__'


class FlashcardDeckListSerializer(serializers.ModelSerializer):
    """List view for flashcard decks"""
    
    card_count = serializers.ReadOnlyField()
    
    class Meta:
        model = FlashcardDeck
        fields = [
            'id', 'name', 'description', 'category', 'level',
            'icon', 'color', 'is_official', 'card_count'
        ]


class FlashcardSerializer(serializers.ModelSerializer):
    """Flashcard serializer with word info"""
    
    word_text = serializers.CharField(source='word.text', read_only=True)
    word_ipa = serializers.CharField(source='word.ipa', read_only=True)
    
    class Meta:
        model = Flashcard
        fields = [
            'id', 'front_text', 'front_type', 'back_text',
            'back_example', 'back_note', 'hint', 'difficulty',
            'audio_url', 'image_url', 'word_text', 'word_ipa'
        ]


class FlashcardDeckDetailSerializer(serializers.ModelSerializer):
    """Detailed deck view with flashcards"""
    
    flashcards = FlashcardSerializer(many=True, read_only=True)
    card_count = serializers.ReadOnlyField()
    
    class Meta:
        model = FlashcardDeck
        fields = [
            'id', 'name', 'description', 'category', 'level',
            'icon', 'color', 'is_official', 'card_count', 'flashcards'
        ]


class UserFlashcardProgressSerializer(serializers.ModelSerializer):
    """User progress on individual flashcard"""
    
    flashcard_text = serializers.CharField(source='flashcard.front_text', read_only=True)
    accuracy = serializers.ReadOnlyField()
    is_due = serializers.ReadOnlyField()
    
    class Meta:
        model = UserFlashcardProgress
        fields = [
            'id', 'flashcard', 'flashcard_text', 
            'easiness_factor', 'interval', 'repetitions',
            'next_review_date', 'last_reviewed_at', 'last_quality',
            'total_reviews', 'total_correct', 'total_incorrect',
            'streak', 'best_streak', 'accuracy',
            'is_learning', 'is_mastered', 'is_due'
        ]
        read_only_fields = [
            'easiness_factor', 'interval', 'repetitions',
            'next_review_date', 'last_reviewed_at',
            'total_reviews', 'total_correct', 'total_incorrect',
            'streak', 'best_streak'
        ]


class ReviewFlashcardSerializer(serializers.Serializer):
    """Serializer for submitting flashcard review"""
    
    quality = serializers.IntegerField(min_value=0, max_value=5)


class StudySessionSerializer(serializers.ModelSerializer):
    """Study session serializer"""
    
    deck_name = serializers.CharField(source='deck.name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = StudySession
        fields = [
            'id', 'deck', 'deck_name', 'started_at', 'ended_at',
            'cards_studied', 'cards_correct', 'cards_incorrect', 'cards_skipped',
            'accuracy', 'time_spent_seconds', 'average_time_per_card',
            'duration_minutes', 'notes'
        ]
        read_only_fields = [
            'started_at', 'ended_at', 'accuracy',
            'time_spent_seconds', 'average_time_per_card'
        ]


class StudyStatsSerializer(serializers.Serializer):
    """Overall study statistics for dashboard"""
    
    total_words_learned = serializers.IntegerField()
    words_mastered = serializers.IntegerField()
    words_learning = serializers.IntegerField()
    total_study_time_minutes = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    average_accuracy = serializers.FloatField()
    current_streak = serializers.IntegerField()
    best_streak = serializers.IntegerField()
    cards_due_today = serializers.IntegerField()
