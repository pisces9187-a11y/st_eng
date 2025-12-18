"""
Admin configuration for Curriculum app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Course, Unit, Lesson, Sentence, Flashcard, GrammarRule,
    PhonemeCategory, Phoneme, PhonemeWord, MinimalPair,
    PronunciationLesson, TongueTwister,
    AudioSource, AudioCache, AudioVersion
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
    
    actions = ['set_as_preferred', 'clear_cache', 'generate_tts_audio', 'regenerate_tts_audio']
    
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
        # Handle new objects without cached_until set
        if not hasattr(obj, 'cached_until') or obj.cached_until is None:
            return format_html(
                '<div style="padding: 12px; background: #f3f4f6; border-radius: 6px; '
                'border-left: 4px solid #9ca3af;">'
                '<strong style="color: #374151;">No Cache Info</strong><br>'
                '<span style="color: #6b7280;">Not yet cached</span>'
                '</div>'
            )
        
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
    
    def generate_tts_audio(self, request, queryset):
        """
        Generate TTS audio for selected phonemes (only if missing).
        Phase 3 Day 5-6 implementation.
        """
        from apps.curriculum.tasks import generate_audio_batch
        
        phoneme_ids = []
        
        for audio in queryset:
            phoneme = audio.phoneme
            
            # Check if TTS audio already exists
            has_tts = AudioSource.objects.filter(
                phoneme=phoneme,
                source_type='tts',
                cached_until__gt=timezone.now()
            ).exists()
            
            if not has_tts:
                phoneme_ids.append(phoneme.id)
        
        if not phoneme_ids:
            self.message_user(
                request,
                "All selected phonemes already have TTS audio",
                level='INFO'
            )
            return
        
        # Start batch generation task
        task = generate_audio_batch.delay(phoneme_ids)
        
        self.message_user(
            request,
            f"Started TTS generation for {len(phoneme_ids)} phonemes. "
            f"Task ID: {task.id}",
            level='SUCCESS'
        )
    generate_tts_audio.short_description = "Generate TTS audio (if missing)"
    
    def regenerate_tts_audio(self, request, queryset):
        """
        Regenerate TTS audio for selected phonemes (force overwrite).
        Phase 3 Day 5-6 implementation.
        """
        from apps.curriculum.tasks import generate_phoneme_audio
        from celery import group
        
        phoneme_ids = [audio.phoneme.id for audio in queryset]
        
        # Start batch generation with force_regenerate=True
        job = group(
            generate_phoneme_audio.s(pid, force_regenerate=True)
            for pid in phoneme_ids
        )
        result = job.apply_async()
        
        self.message_user(
            request,
            f"Started TTS regeneration for {len(phoneme_ids)} phonemes. "
            f"Check Celery logs for progress.",
            level='SUCCESS'
        )
    regenerate_tts_audio.short_description = "Regenerate TTS audio (force)"
    
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


# =============================================================================
# PHONEME ADMIN - With TTS Generation
# =============================================================================

@admin.register(Phoneme)
class PhonemeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Admin interface for managing Phonemes.
    Includes bulk TTS generation action and CSV import/export.
    """
    
    # Import/Export configuration
    resource_class = None  # Will use default
    
    list_display = [
        'ipa_symbol_display',
        'vietnamese_approx',
        'phoneme_type',
        'has_audio_display',
        'pair_count_display',
        'category'
    ]
    
    list_filter = [
        'phoneme_type',
        'category',
        'is_active',
        'voicing'
    ]
    
    search_fields = [
        'ipa_symbol',
        'vietnamese_approx',
        'phoneme_type'
    ]
    
    fieldsets = (
        (_('Phoneme Info'), {
            'fields': (
                'ipa_symbol',
                'vietnamese_approx',
                'phoneme_type',
                'category'
            )
        }),
        (_('Details'), {
            'fields': (
                'voicing',
                'mouth_position',
                'tongue_position_vi',
                'pronunciation_tips_vi',
                'common_mistakes_vi'
            )
        }),
        (_('Audio'), {
            'fields': (
                'preferred_audio_source',
            ),
            'description': 'Select preferred audio source'
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = []
    actions = ['generate_tts_for_phonemes']
    
    def ipa_symbol_display(self, obj):
        """Display IPA symbol with nice formatting."""
        return f"/{obj.ipa_symbol}/"
    ipa_symbol_display.short_description = 'IPA Symbol'
    ipa_symbol_display.admin_order_field = 'ipa_symbol'
    
    def has_audio_display(self, obj):
        """Show if phoneme has audio."""
        has_audio = obj.audio_sources.filter(
            source_type='tts',
            cached_until__gt=timezone.now()
        ).exists()
        
        if has_audio:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">'
                '<i class="fas fa-check-circle"></i> Yes</span>'
            )
        else:
            return format_html(
                '<span style="color: #ef4444; font-weight: bold;">'
                '<i class="fas fa-times-circle"></i> No</span>'
            )
    has_audio_display.short_description = 'Has TTS Audio'
    
    def pair_count_display(self, obj):
        """Show count of minimal pairs for this phoneme."""
        count = MinimalPair.objects.filter(
            phoneme_1=obj
        ).count() + MinimalPair.objects.filter(
            phoneme_2=obj
        ).count()
        
        if count >= 5:
            color = '#10b981'
        elif count >= 3:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} pairs</span>',
            color, count
        )
    pair_count_display.short_description = 'Minimal Pairs'
    
    def generate_tts_for_phonemes(self, request, queryset):
        """
        Bulk action to generate TTS audio for selected phonemes.
        Phase 3 Implementation.
        """
        from apps.curriculum.tasks import generate_audio_batch
        from celery.exceptions import Retry
        
        phoneme_ids = list(queryset.values_list('id', flat=True))
        
        if not phoneme_ids:
            self.message_user(
                request,
                "Please select at least one phoneme.",
                level='WARNING'
            )
            return
        
        try:
            # Start batch TTS generation task
            task = generate_audio_batch.delay(phoneme_ids)
            
            self.message_user(
                request,
                f"✅ Started TTS generation for {len(phoneme_ids)} phoneme(s). "
                f"Task ID: {task.id}. Check Celery worker logs for progress.",
                level='SUCCESS'
            )
        except Retry as e:
            # Handle Celery retry exception (usually network/API errors)
            self.message_user(
                request,
                f"⚠️ Task queued but will retry: {str(e)[:100]}. "
                f"This usually means TTS API is temporarily unavailable. "
                f"The task will automatically retry.",
                level='WARNING'
            )
        except Exception as e:
            # Handle other exceptions gracefully
            self.message_user(
                request,
                f"❌ Error starting TTS generation: {str(e)[:100]}. "
                f"Please check Celery worker logs.",
                level='ERROR'
            )
    generate_tts_for_phonemes.short_description = (
        "🎵 Generate TTS audio for selected phonemes"
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related(
            'category',
            'preferred_audio_source'
        ).prefetch_related('audio_sources', 'example_words')


# =============================================================================
# AUDIO VERSION ADMIN
# =============================================================================

@admin.register(AudioVersion)
class AudioVersionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing audio versions.
    
    Features:
    - View version history
    - Activate/deactivate versions  
    - Compare versions
    - Track usage analytics
    """
    
    list_display = [
        'version_display',
        'phoneme_link',
        'audio_preview',
        'status_badge',
        'quality_badge',
        'usage_stats',
        'duration_text_display',
        'uploaded_info'
    ]
    
    list_filter = [
        'is_active',
        'audio_source__source_type',
        'audio_source__voice_id',
        'effective_from',
    ]
    
    search_fields = [
        'phoneme__ipa_symbol',
        'phoneme__vietnamese_approx',
        'change_reason',
        'uploaded_by__email'
    ]
    
    readonly_fields = [
        'version_number',
        'upload_date',
        'usage_count',
        'audio_player_full',
        'version_history_table'
    ]
    
    fieldsets = (
        ('Version Info', {
            'fields': (
                'phoneme',
                'audio_source',
                'version_number',
                'is_active'
            )
        }),
        ('Audio Player', {
            'fields': ('audio_player_full',)
        }),
        ('Time Tracking', {
            'fields': (
                'effective_from',
                'effective_until',
                'upload_date'
            )
        }),
        ('Metadata', {
            'fields': (
                'uploaded_by',
                'change_reason'
            )
        }),
        ('Analytics', {
            'fields': (
                'usage_count',
                'avg_user_rating',
                'user_rating_count'
            ),
            'classes': ('collapse',)
        }),
        ('Version History', {
            'fields': ('version_history_table',),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'activate_selected_versions',
        'deactivate_selected_versions'
    ]
    
    # Custom displays
    
    def version_display(self, obj):
        """Show version with icon"""
        icon = '🎯' if obj.is_active else '📦'
        return format_html(
            '{} <strong>v{}</strong>',
            icon, obj.version_number
        )
    version_display.short_description = 'Version'
    version_display.admin_order_field = 'version_number'
    
    def phoneme_link(self, obj):
        """Link to phoneme detail"""
        from django.urls import reverse
        url = reverse('admin:curriculum_phoneme_change', args=[obj.phoneme.pk])
        return format_html(
            '<a href="{}" style="font-size: 18px;">/{}/</a><br>'
            '<small style="color: #666;">{}</small>',
            url,
            obj.phoneme.ipa_symbol,
            obj.phoneme.vietnamese_approx
        )
    phoneme_link.short_description = 'Phoneme'
    
    def audio_preview(self, obj):
        """Compact audio player"""
        if obj.audio_source and obj.audio_source.audio_file:
            return format_html(
                '<audio controls preload="none" style="width: 200px; height: 32px;">'
                '<source src="{}" type="audio/mpeg"></audio>',
                obj.audio_source.audio_file.url
            )
        return format_html('<span style="color: #999;">No audio</span>')
    audio_preview.short_description = 'Audio'
    
    def status_badge(self, obj):
        """Active/Inactive badge"""
        if obj.is_active:
            return format_html(
                '<span style="background: #10b981; color: white; '
                'padding: 4px 12px; border-radius: 12px; font-weight: 600;">'
                '✓ ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background: #6b7280; color: white; '
                'padding: 4px 12px; border-radius: 12px;">'
                '✗ INACTIVE</span>'
            )
    status_badge.short_description = 'Status'
    
    def quality_badge(self, obj):
        """Quality score from AudioSource"""
        score = obj.audio_source.get_quality_score()
        source_type = obj.audio_source.get_source_type_display()
        
        if score >= 95:
            color = '#10b981'
            icon = '⭐'
        elif score >= 85:
            color = '#f59e0b'
            icon = '✓'
        else:
            color = '#ef4444'
            icon = '⚠'
        
        return format_html(
            '<span style="display: inline-flex; align-items: center; gap: 4px; '
            'background: {}; color: white; padding: 4px 10px; border-radius: 12px; '
            'font-size: 12px; font-weight: 600;">{} {}%</span><br>'
            '<small style="color: #666;">{}</small>',
            color, icon, score, source_type
        )
    quality_badge.short_description = 'Quality'
    
    def usage_stats(self, obj):
        """Usage statistics"""
        count = obj.usage_count
        
        if count > 1000:
            color = '#10b981'
            label = 'Very Popular'
        elif count > 100:
            color = '#f59e0b'
            label = 'Popular'
        else:
            color = '#6b7280'
            label = 'New'
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 20px; font-weight: bold; color: {};">{}</div>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            color, count, label
        )
    usage_stats.short_description = 'Usage'
    
    def duration_text_display(self, obj):
        """How long active"""
        return obj.get_duration_text()
    duration_text_display.short_description = 'Duration'
    
    def uploaded_info(self, obj):
        """Who uploaded and when"""
        if obj.uploaded_by:
            user_name = obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        else:
            user_name = 'System'
        
        return format_html(
            '<div><strong>{}</strong></div>'
            '<small style="color: #666;">{}</small>',
            user_name,
            obj.upload_date.strftime('%Y-%m-%d %H:%M')
        )
    uploaded_info.short_description = 'Uploaded By'
    
    # Readonly field displays
    
    def audio_player_full(self, obj):
        """Full-width audio player"""
        if obj.audio_source and obj.audio_source.audio_file:
            return format_html(
                '<audio controls preload="metadata" style="width: 100%; max-width: 600px;">'
                '<source src="{}" type="audio/mpeg">'
                'Your browser does not support audio.</audio>'
                '<div style="margin-top: 8px; color: #666; font-size: 13px;">'
                'File: {}<br>'
                'Duration: {:.1f}s</div>',
                obj.audio_source.audio_file.url,
                obj.audio_source.audio_file.name,
                obj.audio_source.audio_duration
            )
        return format_html('<p style="color: #999;">No audio file</p>')
    audio_player_full.short_description = 'Audio Player'
    
    def version_history_table(self, obj):
        """Show all versions for this phoneme"""
        from .models import AudioVersion
        
        versions = AudioVersion.objects.filter(
            phoneme=obj.phoneme
        ).select_related('audio_source', 'uploaded_by').order_by('-version_number')
        
        if not versions:
            return 'No version history'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '''
        <thead style="background: #f3f4f6;">
            <tr>
                <th style="padding: 8px; text-align: left;">Version</th>
                <th style="padding: 8px; text-align: left;">Status</th>
                <th style="padding: 8px; text-align: left;">Quality</th>
                <th style="padding: 8px; text-align: left;">Usage</th>
                <th style="padding: 8px; text-align: left;">Uploaded</th>
            </tr>
        </thead>
        <tbody>
        '''
        
        for v in versions:
            status_badge = '✓ Active' if v.is_active else '✗ Inactive'
            status_color = '#10b981' if v.is_active else '#6b7280'
            
            quality = v.audio_source.get_quality_score()
            
            html += f'''
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 8px;"><strong>v{v.version_number}</strong></td>
                <td style="padding: 8px;">
                    <span style="color: {status_color};">{status_badge}</span>
                </td>
                <td style="padding: 8px;">{quality}%</td>
                <td style="padding: 8px;">{v.usage_count}</td>
                <td style="padding: 8px;">{v.upload_date.strftime("%Y-%m-%d")}</td>
            </tr>
            '''
        
        html += '</tbody></table>'
        
        return format_html(html)
    version_history_table.short_description = 'Version History'
    
    # Actions
    
    def activate_selected_versions(self, request, queryset):
        """Activate selected versions"""
        for version in queryset:
            version.activate(
                user=request.user,
                reason=f"Activated by admin via bulk action"
            )
        
        self.message_user(
            request,
            f"Successfully activated {queryset.count()} version(s)"
        )
    activate_selected_versions.short_description = "✓ Activate selected versions"
    
    def deactivate_selected_versions(self, request, queryset):
        """Deactivate selected versions"""
        queryset.update(
            is_active=False,
            effective_until=timezone.now()
        )
        
        self.message_user(
            request,
            f"Successfully deactivated {queryset.count()} version(s)"
        )
    deactivate_selected_versions.short_description = "✗ Deactivate selected versions"


# =============================================================================
# MINIMAL PAIR ADMIN
# =============================================================================

class MinimalPairResource(resources.ModelResource):
    """Resource for importing/exporting Minimal Pairs"""
    
    class Meta:
        model = MinimalPair
        fields = ('id', 'phoneme_1__ipa_symbol', 'phoneme_2__ipa_symbol',
                  'word_1', 'word_2', 'word_1_ipa', 'word_2_ipa',
                  'word_1_meaning', 'word_2_meaning', 'difficulty',
                  'difference_note', 'order')
        export_order = fields


@admin.register(MinimalPair)
class MinimalPairAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Admin interface for managing Minimal Pairs with autocomplete.
    
    Features:
    - Autocomplete for phoneme selection (type 'p' → see /p/)
    - CSV import/export
    - Bulk actions
    - Audio preview
    """
    
    resource_class = MinimalPairResource
    
    # Enable autocomplete for phoneme fields
    autocomplete_fields = ['phoneme_1', 'phoneme_2']
    
    list_display = [
        'pair_display',
        'phonemes_display',
        'difficulty_badge',
        'audio_status',
        'order'
    ]
    
    list_filter = [
        'difficulty',
        'phoneme_1__phoneme_type',
        'phoneme_2__phoneme_type'
    ]
    
    search_fields = [
        'word_1',
        'word_2',
        'phoneme_1__ipa_symbol',
        'phoneme_2__ipa_symbol',
        'word_1_meaning',
        'word_2_meaning'
    ]
    
    fieldsets = (
        (_('Phonemes'), {
            'fields': ('phoneme_1', 'phoneme_2'),
            'description': 'Type IPA symbol (e.g., "p") to search. Autocomplete will show: /p/ - pờ'
        }),
        (_('Word 1'), {
            'fields': (
                'word_1',
                'word_1_ipa',
                'word_1_meaning',
                'word_1_audio'
            )
        }),
        (_('Word 2'), {
            'fields': (
                'word_2',
                'word_2_ipa',
                'word_2_meaning',
                'word_2_audio'
            )
        }),
        (_('Metadata'), {
            'fields': (
                'difficulty',
                'difference_note',
                'difference_note_vi',
                'order'
            )
        }),
    )
    
    actions = ['check_audio_quality']
    
    def pair_display(self, obj):
        """Display word pair nicely"""
        return format_html(
            '<strong>{}</strong> ↔ <strong>{}</strong>',
            obj.word_1, obj.word_2
        )
    pair_display.short_description = 'Word Pair'
    
    def phonemes_display(self, obj):
        """Display phoneme comparison"""
        return format_html(
            '<span style="font-family: monospace; background: #f3f4f6; padding: 2px 6px; border-radius: 4px;">'
            '/{}/</span> vs <span style="font-family: monospace; background: #f3f4f6; padding: 2px 6px; border-radius: 4px;">'
            '/{}/</span>',
            obj.phoneme_1.ipa_symbol,
            obj.phoneme_2.ipa_symbol
        )
    phonemes_display.short_description = 'Phonemes'
    
    def difficulty_badge(self, obj):
        """Show difficulty with colored badge"""
        difficulty_map = {
            1: ('⭐', '#10b981', 'Easy'),
            2: ('⭐⭐', '#3b82f6', 'Medium'),
            3: ('⭐⭐⭐', '#f59e0b', 'Hard'),
            4: ('⭐⭐⭐⭐', '#ef4444', 'Very Hard'),
            5: ('⭐⭐⭐⭐⭐', '#991b1b', 'Expert')
        }
        
        icon, color, label = difficulty_map.get(obj.difficulty, ('?', '#6b7280', 'Unknown'))
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">'
            '{} {}</span>',
            color, icon, label
        )
    difficulty_badge.short_description = 'Difficulty'
    
    def audio_status(self, obj):
        """Show if both phonemes have audio"""
        has_audio_1 = obj.phoneme_1.preferred_audio_source is not None
        has_audio_2 = obj.phoneme_2.preferred_audio_source is not None
        
        if has_audio_1 and has_audio_2:
            return format_html(
                '<span style="color: #10b981;">🔊 Both</span>'
            )
        elif has_audio_1 or has_audio_2:
            return format_html(
                '<span style="color: #f59e0b;">🔊 Partial</span>'
            )
        else:
            return format_html(
                '<span style="color: #ef4444;">🔇 None</span>'
            )
    audio_status.short_description = 'Audio'
    
    def check_audio_quality(self, request, queryset):
        """Check if all pairs have good audio"""
        pairs_no_audio = []
        for pair in queryset:
            has_audio_1 = (pair.word_1_audio and pair.word_1_audio.name) or \
                         (pair.phoneme_1.preferred_audio_source is not None)
            has_audio_2 = (pair.word_2_audio and pair.word_2_audio.name) or \
                         (pair.phoneme_2.preferred_audio_source is not None)
            
            if not (has_audio_1 and has_audio_2):
                pairs_no_audio.append(f"{pair.word_1}/{pair.word_2}")
        
        if pairs_no_audio:
            self.message_user(
                request,
                f"⚠️ {len(pairs_no_audio)} pairs missing audio: {', '.join(pairs_no_audio[:5])}...",
                level='WARNING'
            )
        else:
            self.message_user(
                request,
                f"✅ All {queryset.count()} pairs have audio!"
            )
    check_audio_quality.short_description = "🔊 Check audio quality"
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'phoneme_1',
            'phoneme_2',
            'phoneme_1__preferred_audio_source',
            'phoneme_2__preferred_audio_source'
        )
