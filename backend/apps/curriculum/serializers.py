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
