"""
Admin configuration for Curriculum app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import (
    Course, Unit, Lesson, Sentence, Flashcard, GrammarRule,
    PhonemeCategory, Phoneme, PhonemeWord, MinimalPair,
    PronunciationLesson, TongueTwister,
    AudioSource, AudioCache
)


# =============================================================================
# PHASE 1: AUDIO SYSTEM ADMIN
# =============================================================================

class AudioCacheInline(admin.StackedInline):
    """Inline display of AudioCache stats."""
    model = AudioCache
    extra = 0
    readonly_fields = [
        'file_size_display',
        'generated_at',
        'last_accessed_at',
        'usage_count',
        'age_display'
    ]
    can_delete = False
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        if obj and obj.file_size:
            size = obj.file_size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:.2f} KB"
            else:
                return f"{size / (1024 * 1024):.2f} MB"
        return "Unknown"
    file_size_display.short_description = 'File Size'
    
    def age_display(self, obj):
        """Display cache age."""
        if obj:
            days = obj.get_age_days()
            if days == 0:
                return "Today"
            elif days == 1:
                return "1 day ago"
            else:
                return f"{days} days ago"
        return "-"
    age_display.short_description = 'Cache Age'


@admin.register(AudioSource)
class AudioSourceAdmin(admin.ModelAdmin):
    """Admin for AudioSource with audio preview and quality indicators."""
    
    list_display = [
        'phoneme_display',
        'source_type',
        'voice_id',
        'audio_preview',
        'quality_badge',
        'usage_count_display',
        'duration_display',
        'cached_status'
    ]
    list_filter = ['source_type', 'voice_id', 'language', 'created_at']
    search_fields = [
        'phoneme__ipa_symbol',
        'phoneme__vietnamese_approx',
        'voice_id'
    ]
    readonly_fields = [
        'audio_player',
        'quality_score_display',
        'created_at',
        'updated_at',
        'cache_status_display'
    ]
    inlines = [AudioCacheInline]
    raw_id_fields = ['phoneme']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('phoneme', 'source_type', 'audio_file', 'audio_player')
        }),
        (_('TTS Settings'), {
            'fields': ('voice_id', 'language', 'metadata'),
            'classes': ('collapse',)
        }),
        (_('Audio Info'), {
            'fields': ('audio_duration', 'quality_score_display')
        }),
        (_('Cache Settings'), {
            'fields': ('cached_until', 'cache_status_display'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['set_as_preferred', 'clear_cache']
    
    def phoneme_display(self, obj):
        """Show phoneme with IPA symbol."""
        return f"/{obj.phoneme.ipa_symbol}/"
    phoneme_display.short_description = 'Phoneme'
    phoneme_display.admin_order_field = 'phoneme__ipa_symbol'
    
    def audio_preview(self, obj):
        """Show compact audio player in list view."""
        if obj.audio_file:
            return format_html(
                '<audio controls preload="none" style="width: 180px; height: 32px;"'
                ' controlsList="nodownload noplaybackrate">'
                '<source src="{}" type="audio/mpeg"></audio>',
                obj.audio_file.url
            )
        return format_html('<span style="color: #999;">No audio</span>')
    audio_preview.short_description = 'Preview'
    
    def audio_player(self, obj):
        """Full audio player in detail view."""
        if obj.audio_file:
            return format_html(
                '<audio controls preload="metadata" style="width: 100%; max-width: 500px;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio.</audio>'
                '<div style="margin-top: 8px; color: #666; font-size: 13px;">'
                'File: {}</div>',
                obj.audio_file.url,
                obj.audio_file.name
            )
        return format_html('<p style="color: #999;">No audio file uploaded</p>')
    audio_player.short_description = 'Audio Player'
    
    def quality_badge(self, obj):
        """Show quality score badge with color."""
        score = obj.get_quality_score()
        if score >= 95:
            color = '#10b981'  # green
            icon = '⭐'
        elif score >= 85:
            color = '#f59e0b'  # orange
            icon = '✓'
        else:
            color = '#ef4444'  # red
            icon = '⚠'
        
        return format_html(
            '<span style="display: inline-flex; align-items: center; gap: 4px; '
            'background: {}; color: white; padding: 4px 10px; border-radius: 12px; '
            'font-size: 12px; font-weight: 600;">{} {}%</span>',
            color, icon, score
        )
    quality_badge.short_description = 'Quality'
    quality_badge.admin_order_field = 'source_type'
    
    def quality_score_display(self, obj):
        """Detailed quality info."""
        score = obj.get_quality_score()
        source_type = obj.get_source_type_display()
        
        descriptions = {
            100: '🌟 Excellent - Native speaker recording',
            90: '✅ Very Good - High-quality TTS (cached)',
            80: '⚡ Good - On-demand TTS generation'
        }
        
        desc = descriptions.get(score, 'Unknown')
        
        return format_html(
            '<div style="padding: 12px; background: #f3f4f6; border-radius: 6px;">'
            '<div style="font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 4px;">'
            '{}%</div>'
            '<div style="color: #6b7280; font-size: 14px; margin-bottom: 8px;">'
            '{}</div>'
            '<div style="color: #4b5563; font-size: 13px;">{}</div>'
            '</div>',
            score, source_type, desc
        )
    quality_score_display.short_description = 'Quality Score'
    
    def usage_count_display(self, obj):
        """Show usage count from cache."""
        if hasattr(obj, 'cache'):
            count = obj.cache.usage_count
            if count > 100:
                return format_html(
                    '<span style="color: #10b981; font-weight: bold;">{}</span>',
                    count
                )
            elif count > 10:
                return format_html('<span style="color: #f59e0b;">{}</span>', count)
            else:
                return format_html('<span style="color: #6b7280;">{}</span>', count)
        return format_html('<span style="color: #999;">-</span>')
    usage_count_display.short_description = 'Usage'
    
    def duration_display(self, obj):
        """Show audio duration."""
        if obj.audio_duration:
            return f"{obj.audio_duration:.1f}s"
        return "-"
    duration_display.short_description = 'Duration'
    
    def cached_status(self, obj):
        """Show cache status."""
        if obj.is_native():
            return format_html(
                '<span style="color: #10b981; font-weight: 500;">✓ Permanent</span>'
            )
        elif obj.is_cached():
            days_left = (obj.cached_until - timezone.now()).days
            return format_html(
                '<span style="color: #10b981;">✓ Cached ({} days)</span>',
                days_left
            )
        else:
            return format_html(
                '<span style="color: #ef4444;">✗ Expired</span>'
            )
    cached_status.short_description = 'Cache'
    
    def cache_status_display(self, obj):
        """Detailed cache status."""
        if obj.is_native():
            return format_html(
                '<div style="padding: 12px; background: #d1fae5; border-radius: 6px; '
                'border-left: 4px solid #10b981;">'
                '<strong style="color: #065f46;">Native Audio</strong><br>'
                '<span style="color: #047857;">Permanent - never expires</span>'
                '</div>'
            )
        elif obj.is_cached():
            days_left = (obj.cached_until - timezone.now()).days
            return format_html(
                '<div style="padding: 12px; background: #dbeafe; border-radius: 6px; '
                'border-left: 4px solid #3b82f6;">'
                '<strong style="color: #1e40af;">TTS Cached</strong><br>'
                '<span style="color: #1d4ed8;">Valid for {} more days</span><br>'
                '<span style="color: #6b7280; font-size: 12px;">Expires: {}</span>'
                '</div>',
                days_left,
                obj.cached_until.strftime('%Y-%m-%d %H:%M')
            )
        else:
            return format_html(
                '<div style="padding: 12px; background: #fee2e2; border-radius: 6px; '
                'border-left: 4px solid #ef4444;">'
                '<strong style="color: #991b1b;">Cache Expired</strong><br>'
                '<span style="color: #b91c1c;">Needs regeneration</span>'
                '</div>'
            )
    cache_status_display.short_description = 'Cache Status'
    
    def set_as_preferred(self, request, queryset):
        """Set selected audio as preferred for their phonemes."""
        count = 0
        for audio in queryset:
            phoneme = audio.phoneme
            phoneme.preferred_audio_source = audio
            phoneme.save(update_fields=['preferred_audio_source'])
            count += 1
        
        self.message_user(
            request,
            f"Set {count} audio source(s) as preferred for their phonemes."
        )
    set_as_preferred.short_description = "Set as preferred audio for phoneme"
    
    def clear_cache(self, request, queryset):
        """Clear cache for selected audio sources."""
        count = queryset.filter(source_type='tts').update(
            cached_until=timezone.now()
        )
        self.message_user(
            request,
            f"Cleared cache for {count} TTS audio source(s)."
        )
    clear_cache.short_description = "Clear cache (TTS only)"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'phoneme',
            'phoneme__category'
        ).prefetch_related('cache')


# =============================================================================
# ORIGINAL ADMIN CLASSES
# =============================================================================

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
