"""
Admin configuration for Curriculum app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Course, Unit, Lesson, Sentence, Flashcard, GrammarRule


class UnitInline(admin.TabularInline):
    """Inline for Units in Course admin."""
    model = Unit
    extra = 0
    fields = ['title', 'topic', 'order', 'status']
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin for Course."""
    
    list_display = [
        'title', 'cefr_level', 'status', 'is_free', 'is_featured',
        'total_units', 'order', 'created_at'
    ]
    list_filter = ['cefr_level', 'status', 'is_free', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['cefr_level', 'order', 'title']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'thumbnail')
        }),
        (_('Level & Requirements'), {
            'fields': ('cefr_level', 'estimated_hours')
        }),
        (_('Status & Visibility'), {
            'fields': ('status', 'is_free', 'is_featured', 'order')
        }),
        (_('Timestamps'), {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    inlines = [UnitInline]
    
    def total_units(self, obj):
        return obj.total_units
    total_units.short_description = 'Units'


class LessonInline(admin.TabularInline):
    """Inline for Lessons in Unit admin."""
    model = Lesson
    extra = 0
    fields = ['title', 'lesson_type', 'difficulty', 'order', 'status']
    show_change_link = True


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin for Unit."""
    
    list_display = [
        'title', 'course', 'topic', 'status', 
        'total_lessons', 'order', 'created_at'
    ]
    list_filter = ['status', 'course__cefr_level', 'course', 'created_at']
    search_fields = ['title', 'description', 'topic', 'course__title']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['course']
    ordering = ['course', 'order', 'title']
    
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'slug', 'description', 'thumbnail')
        }),
        (_('Settings'), {
            'fields': ('topic', 'status', 'order')
        }),
    )
    
    inlines = [LessonInline]
    
    def total_lessons(self, obj):
        return obj.total_lessons
    total_lessons.short_description = 'Lessons'


class SentenceInline(admin.TabularInline):
    """Inline for Sentences in Lesson admin."""
    model = Sentence
    extra = 0
    fields = ['text_content', 'text_vi', 'order']
    show_change_link = True


class FlashcardInline(admin.TabularInline):
    """Inline for Flashcards in Lesson admin."""
    model = Flashcard
    extra = 0
    fields = ['front_text', 'back_text', 'card_type', 'order']
    show_change_link = True


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin for Lesson."""
    
    list_display = [
        'title', 'unit', 'lesson_type', 'difficulty',
        'estimated_minutes', 'xp_reward', 'status', 'is_premium', 'order'
    ]
    list_filter = [
        'lesson_type', 'status', 'is_premium', 'difficulty',
        'unit__course__cefr_level', 'created_at'
    ]
    search_fields = ['title', 'description', 'unit__title', 'unit__course__title']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['unit']
    ordering = ['unit', 'order', 'title']
    
    fieldsets = (
        (None, {
            'fields': ('unit', 'title', 'slug', 'description', 'thumbnail')
        }),
        (_('Content'), {
            'fields': ('lesson_type', 'content_html', 'objectives')
        }),
        (_('Settings'), {
            'fields': (
                'difficulty', 'estimated_minutes', 'xp_reward',
                'status', 'is_premium', 'order'
            )
        }),
    )
    
    inlines = [SentenceInline, FlashcardInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('unit', 'unit__course')


@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    """Admin for Sentence."""
    
    list_display = [
        'short_text', 'lesson', 'sentence_type', 
        'has_audio', 'has_ipa', 'order'
    ]
    list_filter = ['sentence_type', 'lesson__lesson_type', 'created_at']
    search_fields = ['text_content', 'text_vi', 'lesson__title']
    raw_id_fields = ['lesson']
    ordering = ['lesson', 'order']
    
    fieldsets = (
        (None, {
            'fields': ('lesson', 'text_content', 'text_vi', 'context')
        }),
        (_('Audio'), {
            'fields': ('audio_file', 'audio_slow', 'audio_duration')
        }),
        (_('Phonetics & Grammar'), {
            'fields': ('ipa_transcription', 'grammar_analysis', 'vocabulary_highlights')
        }),
        (_('Settings'), {
            'fields': ('sentence_type', 'order')
        }),
    )
    
    def short_text(self, obj):
        text = obj.text_content[:60]
        if len(obj.text_content) > 60:
            text += '...'
        return text
    short_text.short_description = 'Nội dung'
    
    def has_audio(self, obj):
        return bool(obj.audio_file)
    has_audio.boolean = True
    has_audio.short_description = 'Audio'
    
    def has_ipa(self, obj):
        return bool(obj.ipa_transcription)
    has_ipa.boolean = True
    has_ipa.short_description = 'IPA'


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    """Admin for Flashcard."""
    
    list_display = [
        'short_front', 'card_type', 'lesson', 
        'difficulty', 'is_active', 'order'
    ]
    list_filter = ['card_type', 'difficulty', 'is_active', 'created_at']
    search_fields = ['front_text', 'back_text', 'lesson__title']
    raw_id_fields = ['lesson', 'sentence']
    ordering = ['lesson', 'order']
    
    fieldsets = (
        (None, {
            'fields': ('lesson', 'sentence', 'front_text', 'back_text')
        }),
        (_('Media'), {
            'fields': ('front_audio', 'front_image')
        }),
        (_('Additional Info'), {
            'fields': ('ipa', 'part_of_speech', 'examples', 'tags')
        }),
        (_('Settings'), {
            'fields': ('card_type', 'difficulty', 'is_active', 'order')
        }),
    )
    
    def short_front(self, obj):
        text = obj.front_text[:40]
        if len(obj.front_text) > 40:
            text += '...'
        return text
    short_front.short_description = 'Mặt trước'


@admin.register(GrammarRule)
class GrammarRuleAdmin(admin.ModelAdmin):
    """Admin for GrammarRule."""
    
    list_display = [
        'title', 'category', 'cefr_level', 
        'is_active', 'order', 'created_at'
    ]
    list_filter = ['category', 'cefr_level', 'is_active', 'created_at']
    search_fields = ['title', 'explanation_html', 'explanation_vi', 'structure']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['related_rules']
    ordering = ['category', 'order', 'title']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'cefr_level')
        }),
        (_('Content'), {
            'fields': ('structure', 'explanation_html', 'explanation_vi')
        }),
        (_('Examples'), {
            'fields': ('examples', 'common_mistakes')
        }),
        (_('Relations'), {
            'fields': ('related_rules',)
        }),
        (_('Settings'), {
            'fields': ('is_active', 'order')
        }),
    )
