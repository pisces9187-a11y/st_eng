"""
Serializers for Curriculum app.

Handles serialization for Course, Unit, Lesson, Sentence, Flashcard,
GrammarRule, and Phase 1 Audio System (AudioSource, Phoneme).
"""

from rest_framework import serializers

from .models import (
    Course, Unit, Lesson, Sentence, Flashcard, GrammarRule,
    Phoneme, PhonemeCategory, AudioSource, AudioCache
)

# Import UserPhonemeProgress for pronunciation serializers
from apps.users.models import UserPhonemeProgress


# =============================================================================
# PHASE 1: AUDIO SYSTEM SERIALIZERS
# =============================================================================

class AudioCacheSerializer(serializers.ModelSerializer):
    """Serializer for AudioCache usage stats."""
    
    age_days = serializers.IntegerField(source='get_age_days', read_only=True)
    is_stale = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = AudioCache
        fields = [
            'file_size',
            'file_size_mb',
            'generated_at',
            'last_accessed_at',
            'usage_count',
            'age_days',
            'is_stale'
        ]
    
    def get_file_size_mb(self, obj):
        """Convert bytes to MB."""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0
    
    def get_is_stale(self, obj):
        """Check if cache is stale (> 30 days)."""
        return obj.is_stale(max_days=30)


class AudioSourceSerializer(serializers.ModelSerializer):
    """Serializer for AudioSource with quality and cache info."""
    
    audio_url = serializers.SerializerMethodField()
    quality_score = serializers.IntegerField(source='get_quality_score', read_only=True)
    is_native = serializers.BooleanField(read_only=True)
    is_cached = serializers.BooleanField(read_only=True)
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    cache_info = AudioCacheSerializer(source='cache', read_only=True)
    
    class Meta:
        model = AudioSource
        fields = [
            'id',
            'source_type',
            'source_type_display',
            'voice_id',
            'language',
            'audio_file',
            'audio_url',
            'audio_duration',
            'quality_score',
            'is_native',
            'is_cached',
            'cached_until',
            'cache_info',
            'created_at',
            'updated_at'
        ]
    
    def get_audio_url(self, obj):
        """Get full audio URL."""
        return obj.get_url()


class PhonemeMinimalSerializer(serializers.ModelSerializer):
    """Minimal phoneme serializer for nested usage."""
    
    phoneme_type_display = serializers.CharField(source='get_phoneme_type_display', read_only=True)
    
    class Meta:
        model = Phoneme
        fields = [
            'id',
            'ipa_symbol',
            'vietnamese_approx',
            'phoneme_type',
            'phoneme_type_display'
        ]


class PhonemeAudioSerializer(serializers.Serializer):
    """Serializer for phoneme with audio (nested response)."""
    
    phoneme = PhonemeMinimalSerializer(read_only=True)
    audio = AudioSourceSerializer(read_only=True)
    alternatives = AudioSourceSerializer(many=True, read_only=True)


class AudioQualityReportSerializer(serializers.Serializer):
    """Serializer for audio quality report."""
    
    total_phonemes = serializers.IntegerField()
    phonemes_with_audio = serializers.IntegerField()
    phonemes_without_audio = serializers.IntegerField()
    coverage_percent = serializers.FloatField()
    
    native_audio_count = serializers.IntegerField()
    tts_audio_count = serializers.IntegerField()
    generated_audio_count = serializers.IntegerField()
    
    avg_quality_score = serializers.FloatField()
    
    cache_enabled = serializers.BooleanField()
    cache_hit_rate = serializers.FloatField(required=False)
    
    by_category = serializers.DictField(required=False)


# =============================================================================
# ORIGINAL SERIALIZERS
# =============================================================================

class FlashcardSerializer(serializers.ModelSerializer):
    """Serializer for Flashcard model."""
    
    card_type_display = serializers.CharField(
        source='get_card_type_display',
        read_only=True
    )
    
    class Meta:
        model = Flashcard
        fields = [
            'id', 'front_text', 'back_text',
            'front_audio', 'front_image', 'ipa',
            'examples', 'part_of_speech',
            'card_type', 'card_type_display',
            'difficulty', 'tags', 'order'
        ]


class FlashcardMinimalSerializer(serializers.ModelSerializer):
    """Minimal flashcard serializer for lists."""
    
    class Meta:
        model = Flashcard
        fields = ['id', 'front_text', 'back_text', 'card_type', 'difficulty']


class SentenceSerializer(serializers.ModelSerializer):
    """Serializer for Sentence model."""
    
    flashcards = FlashcardMinimalSerializer(many=True, read_only=True)
    sentence_type_display = serializers.CharField(
        source='get_sentence_type_display',
        read_only=True
    )
    word_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sentence
        fields = [
            'id', 'text_content', 'text_vi',
            'audio_file', 'audio_slow', 'audio_duration',
            'ipa_transcription', 'grammar_analysis', 'vocabulary_highlights',
            'sentence_type', 'sentence_type_display',
            'context', 'word_count', 'order',
            'flashcards'
        ]


class SentenceMinimalSerializer(serializers.ModelSerializer):
    """Minimal sentence serializer for lists."""
    
    class Meta:
        model = Sentence
        fields = ['id', 'text_content', 'text_vi', 'audio_file', 'order']


class LessonSerializer(serializers.ModelSerializer):
    """Full Lesson serializer with sentences and flashcards."""
    
    sentences = SentenceSerializer(many=True, read_only=True)
    flashcards = FlashcardSerializer(many=True, read_only=True)
    lesson_type_display = serializers.CharField(
        source='get_lesson_type_display',
        read_only=True
    )
    total_sentences = serializers.IntegerField(read_only=True)
    total_flashcards = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField(source='course.id', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    unit_title = serializers.CharField(source='unit.title', read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'lesson_type', 'lesson_type_display', 'difficulty',
            'content_html', 'objectives',
            'estimated_minutes', 'xp_reward',
            'is_premium', 'order',
            'total_sentences', 'total_flashcards',
            'course_id', 'course_title', 'unit_title',
            'sentences', 'flashcards',
            'created_at', 'updated_at'
        ]


class LessonListSerializer(serializers.ModelSerializer):
    """Lesson serializer for list views (without content)."""
    
    lesson_type_display = serializers.CharField(
        source='get_lesson_type_display',
        read_only=True
    )
    total_sentences = serializers.IntegerField(read_only=True)
    total_flashcards = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'lesson_type', 'lesson_type_display', 'difficulty',
            'estimated_minutes', 'xp_reward',
            'is_premium', 'order',
            'total_sentences', 'total_flashcards'
        ]


class UnitSerializer(serializers.ModelSerializer):
    """Full Unit serializer with lessons."""
    
    lessons = LessonListSerializer(many=True, read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'topic', 'order', 'status',
            'total_lessons', 'course_title',
            'lessons',
            'created_at', 'updated_at'
        ]


class UnitListSerializer(serializers.ModelSerializer):
    """Unit serializer for list views."""
    
    total_lessons = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'topic', 'order', 'total_lessons'
        ]


class CourseSerializer(serializers.ModelSerializer):
    """Full Course serializer with units."""
    
    units = UnitListSerializer(many=True, read_only=True)
    cefr_level_display = serializers.CharField(
        source='get_cefr_level_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    total_units = serializers.IntegerField(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'cefr_level', 'cefr_level_display',
            'estimated_hours', 'status', 'status_display',
            'is_free', 'is_featured', 'order',
            'total_units', 'total_lessons',
            'units',
            'created_at', 'updated_at', 'published_at'
        ]


class CourseListSerializer(serializers.ModelSerializer):
    """Course serializer for list views."""
    
    cefr_level_display = serializers.CharField(
        source='get_cefr_level_display',
        read_only=True
    )
    total_units = serializers.IntegerField(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'cefr_level', 'cefr_level_display',
            'estimated_hours', 'is_free', 'is_featured',
            'total_units', 'total_lessons'
        ]


class GrammarRuleSerializer(serializers.ModelSerializer):
    """Full GrammarRule serializer."""
    
    cefr_level_display = serializers.CharField(
        source='get_cefr_level_display',
        read_only=True
    )
    related_rules = serializers.SerializerMethodField()
    
    class Meta:
        model = GrammarRule
        fields = [
            'id', 'title', 'slug', 'category', 'cefr_level', 'cefr_level_display',
            'explanation_html', 'explanation_vi', 'structure',
            'examples', 'common_mistakes',
            'related_rules', 'order',
            'created_at', 'updated_at'
        ]
    
    def get_related_rules(self, obj):
        return GrammarRuleMinimalSerializer(
            obj.related_rules.filter(is_active=True),
            many=True
        ).data


class GrammarRuleMinimalSerializer(serializers.ModelSerializer):
    """Minimal GrammarRule serializer for lists and relations."""
    
    class Meta:
        model = GrammarRule
        fields = ['id', 'title', 'slug', 'category', 'cefr_level']


class GrammarRuleListSerializer(serializers.ModelSerializer):
    """GrammarRule serializer for list views."""
    
    cefr_level_display = serializers.CharField(
        source='get_cefr_level_display',
        read_only=True
    )
    
    class Meta:
        model = GrammarRule
        fields = [
            'id', 'title', 'slug', 'category',
            'cefr_level', 'cefr_level_display',
            'structure'
        ]


# =============================================================================
# PRONUNCIATION LEARNING FLOW SERIALIZERS (Day 2)
# =============================================================================

class UserPhonemeProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for UserPhonemeProgress with stage information.
    Used for tracking user's learning journey.
    """
    phoneme_symbol = serializers.CharField(source='phoneme.ipa_symbol', read_only=True)
    phoneme_category = serializers.CharField(source='phoneme.category.name', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display_vi', read_only=True)
    next_action = serializers.CharField(source='get_next_stage_action', read_only=True)
    can_discriminate = serializers.BooleanField(source='can_practice_discrimination', read_only=True)
    can_produce = serializers.BooleanField(source='can_practice_production', read_only=True)
    
    class Meta:
        model = UserPhonemeProgress
        fields = [
            'id',
            'phoneme',
            'phoneme_symbol',
            'phoneme_category',
            'current_stage',
            'stage_display',
            'next_action',
            'mastery_level',
            # Stage timestamps
            'discovery_date',
            'learning_started_at',
            'discrimination_started_at',
            'production_started_at',
            'mastered_at',
            # Discrimination metrics
            'discrimination_attempts',
            'discrimination_correct',
            'discrimination_accuracy',
            # Production metrics
            'production_attempts',
            'production_best_score',
            # Overall stats
            'times_practiced',
            'accuracy_rate',
            'last_practiced_at',
            # Permissions
            'can_discriminate',
            'can_produce',
        ]
        read_only_fields = [
            'id', 'current_stage', 'discovery_date', 'learning_started_at',
            'discrimination_started_at', 'production_started_at', 'mastered_at',
            'discrimination_attempts', 'discrimination_correct', 'discrimination_accuracy',
            'production_attempts', 'production_best_score',
            'times_practiced', 'accuracy_rate', 'last_practiced_at'
        ]


class DiscriminationQuizQuestionSerializer(serializers.Serializer):
    """Serializer for a single discrimination quiz question."""
    question_number = serializers.IntegerField()
    phoneme_a_id = serializers.IntegerField()
    phoneme_a_symbol = serializers.CharField()
    phoneme_a_example = serializers.CharField()
    phoneme_b_id = serializers.IntegerField()
    phoneme_b_symbol = serializers.CharField()
    phoneme_b_example = serializers.CharField()
    audio_url = serializers.CharField()  # Pre-generated audio URL
    correct_phoneme_id = serializers.IntegerField(write_only=True)  # Hidden from response


class DiscriminationQuizSerializer(serializers.Serializer):
    """Serializer for discrimination quiz (10 questions)."""
    phoneme_id = serializers.IntegerField()
    phoneme_symbol = serializers.CharField()
    total_questions = serializers.IntegerField()
    questions = DiscriminationQuizQuestionSerializer(many=True)
    current_accuracy = serializers.FloatField()  # User's current accuracy (0-1)
    unlock_threshold = serializers.FloatField(default=0.8)  # Need 80% to unlock production


class DiscriminationSubmitSerializer(serializers.Serializer):
    """Serializer for submitting discrimination quiz answers."""
    question_number = serializers.IntegerField()
    selected_phoneme_id = serializers.IntegerField()
    
    def validate_question_number(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Question number must be between 1 and 10.")
        return value


class DiscriminationResultSerializer(serializers.Serializer):
    """Serializer for discrimination quiz result."""
    is_correct = serializers.BooleanField()
    correct_phoneme_id = serializers.IntegerField()
    correct_phoneme_symbol = serializers.CharField()
    selected_phoneme_id = serializers.IntegerField()
    selected_phoneme_symbol = serializers.CharField()
    explanation = serializers.CharField()  # Why this is correct/incorrect
    comparison = serializers.DictField()  # Tongue/mouth position differences
    total_correct = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    accuracy = serializers.FloatField()
    production_unlocked = serializers.BooleanField()


class ProductionReferenceSerializer(serializers.Serializer):
    """Serializer for production practice reference audio."""
    phoneme_id = serializers.IntegerField()
    phoneme_symbol = serializers.CharField()
    reference_audio_url = serializers.CharField()
    audio_duration = serializers.FloatField()  # Duration in seconds
    mouth_diagram_url = serializers.CharField(allow_null=True)
    video_tutorial_url = serializers.CharField(allow_null=True)
    pronunciation_tips = serializers.CharField()
    target_duration_min = serializers.FloatField()
    target_duration_max = serializers.FloatField()


class ProductionSubmitSerializer(serializers.Serializer):
    """Serializer for submitting production recording."""
    audio_file = serializers.FileField()  # User's recording
    duration = serializers.FloatField()  # Recording duration
    
    def validate_audio_file(self, value):
        """Validate audio file size and format."""
        if value.size > 5 * 1024 * 1024:  # 5MB max
            raise serializers.ValidationError("Audio file must be under 5MB.")
        
        allowed_formats = ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/ogg']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError(f"Audio format must be one of: {', '.join(allowed_formats)}")
        
        return value
    
    def validate_duration(self, value):
        """Validate recording duration."""
        if value < 0.1 or value > 10:
            raise serializers.ValidationError("Recording duration must be between 0.1 and 10 seconds.")
        return value


class ProductionResultSerializer(serializers.Serializer):
    """Serializer for production practice result."""
    score = serializers.FloatField()  # 0-1 score
    duration_diff = serializers.FloatField()  # Difference from reference (seconds)
    duration_feedback = serializers.CharField()  # "too short", "good", "too long"
    overall_feedback = serializers.CharField()
    is_best_attempt = serializers.BooleanField()
    attempts_count = serializers.IntegerField()
    best_score = serializers.FloatField()
    mastered = serializers.BooleanField()  # True if reached mastery


class OverallProgressSerializer(serializers.Serializer):
    """Serializer for user's overall pronunciation progress."""
    total_phonemes = serializers.IntegerField()
    
    # Count by stage
    not_started_count = serializers.IntegerField()
    discovered_count = serializers.IntegerField()
    learning_count = serializers.IntegerField()
    discriminating_count = serializers.IntegerField()
    producing_count = serializers.IntegerField()
    mastered_count = serializers.IntegerField()
    
    # Percentage breakdown
    discovery_percentage = serializers.FloatField()
    mastery_percentage = serializers.FloatField()
    
    # Recent activity
    recently_practiced = UserPhonemeProgressSerializer(many=True)
    recommended_next = serializers.ListField()  # List of phoneme IDs to practice next
    
    # Stats
    total_practice_time = serializers.IntegerField()  # Estimated minutes
    current_streak = serializers.IntegerField()  # Days
    avg_discrimination_accuracy = serializers.FloatField()
    avg_production_score = serializers.FloatField()

