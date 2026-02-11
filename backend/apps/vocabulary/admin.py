"""
Vocabulary admin interface
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Word, FlashcardDeck, Flashcard, UserFlashcardProgress, StudySession


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('text', 'pos', 'cefr_level', 'meaning_vi_short', 'frequency_rank')
    list_filter = ('cefr_level', 'pos')
    search_fields = ('text', 'meaning_vi', 'meaning_en')
    ordering = ('frequency_rank', 'text')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('text', 'pos', 'cefr_level', 'frequency_rank', 'register')
        }),
        ('Pronunciation', {
            'fields': ('ipa', 'british_ipa', 'american_ipa', 'audio_uk', 'audio_us')
        }),
        ('Meanings', {
            'fields': ('meaning_vi', 'meaning_en')
        }),
        ('Examples', {
            'fields': ('example_en', 'example_vi')
        }),
        ('Learning Aids', {
            'fields': ('collocations', 'mnemonic', 'etymology', 'synonyms', 'antonyms')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Relationships', {
            'fields': ('phonemes',)
        }),
    )
    
    filter_horizontal = ('phonemes',)
    
    def meaning_vi_short(self, obj):
        return obj.meaning_vi[:50] + '...' if len(obj.meaning_vi) > 50 else obj.meaning_vi
    meaning_vi_short.short_description = 'Vietnamese Meaning'


@admin.register(FlashcardDeck)
class FlashcardDeckAdmin(admin.ModelAdmin):
    list_display = ('name_with_icon', 'category', 'level', 'card_count', 'is_official', 'created_by')
    list_filter = ('category', 'level', 'is_official', 'is_public')
    search_fields = ('name', 'description')
    ordering = ('-is_official', 'level', 'name')
    
    readonly_fields = ('created_at', 'updated_at')
    
    def name_with_icon(self, obj):
        return f"{obj.icon} {obj.name}"
    name_with_icon.short_description = 'Deck Name'


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('front_text', 'deck', 'difficulty', 'front_type', 'order')
    list_filter = ('deck', 'front_type', 'difficulty')
    search_fields = ('front_text', 'back_text')
    ordering = ('deck', 'order')
    
    fieldsets = (
        ('Relationships', {
            'fields': ('word', 'deck')
        }),
        ('Front Side (Question)', {
            'fields': ('front_text', 'front_type', 'hint')
        }),
        ('Back Side (Answer)', {
            'fields': ('back_text', 'back_example', 'back_note')
        }),
        ('Settings', {
            'fields': ('difficulty', 'tags', 'order')
        }),
        ('Media', {
            'fields': ('audio_url', 'image_url')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserFlashcardProgress)
class UserFlashcardProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'flashcard_preview', 'next_review_date', 
        'interval', 'repetitions', 'accuracy_percent', 'status'
    )
    list_filter = ('is_learning', 'is_mastered', 'last_quality')
    search_fields = ('user__username', 'flashcard__front_text')
    ordering = ('next_review_date',)
    
    readonly_fields = (
        'created_at', 'updated_at', 
        'total_reviews', 'total_correct', 'total_incorrect',
        'streak', 'best_streak'
    )
    
    fieldsets = (
        ('Relationships', {
            'fields': ('user', 'flashcard')
        }),
        ('SM-2 Algorithm', {
            'fields': ('easiness_factor', 'interval', 'repetitions')
        }),
        ('Review Schedule', {
            'fields': ('next_review_date', 'last_reviewed_at', 'last_quality')
        }),
        ('Statistics', {
            'fields': (
                'total_reviews', 'total_correct', 'total_incorrect',
                'streak', 'best_streak'
            )
        }),
        ('Status', {
            'fields': ('is_learning', 'is_mastered')
        }),
    )
    
    def flashcard_preview(self, obj):
        return obj.flashcard.front_text[:30]
    flashcard_preview.short_description = 'Flashcard'
    
    def accuracy_percent(self, obj):
        accuracy = obj.accuracy
        color = 'green' if accuracy >= 80 else 'orange' if accuracy >= 60 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, accuracy
        )
    accuracy_percent.short_description = 'Accuracy'
    
    def status(self, obj):
        if obj.is_mastered:
            return format_html('<span style="color: green;">✓ Mastered</span>')
        elif obj.is_learning:
            return format_html('<span style="color: orange;">📚 Learning</span>')
        return 'Not started'
    status.short_description = 'Status'


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'deck', 'started_at', 'duration_display', 
        'cards_studied', 'accuracy_percent', 'avg_time_per_card'
    )
    list_filter = ('deck', 'started_at')
    search_fields = ('user__username', 'deck__name')
    ordering = ('-started_at',)
    
    readonly_fields = (
        'started_at', 'ended_at', 
        'cards_studied', 'cards_correct', 'cards_incorrect', 'cards_skipped',
        'accuracy', 'time_spent_seconds', 'average_time_per_card'
    )
    
    fieldsets = (
        ('Session Info', {
            'fields': ('user', 'deck', 'started_at', 'ended_at')
        }),
        ('Cards', {
            'fields': ('cards_studied', 'cards_correct', 'cards_incorrect', 'cards_skipped')
        }),
        ('Performance', {
            'fields': ('accuracy', 'time_spent_seconds', 'average_time_per_card')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def duration_display(self, obj):
        minutes = obj.duration_minutes
        if minutes == 0:
            return 'In progress'
        return f"{minutes} min"
    duration_display.short_description = 'Duration'
    
    def accuracy_percent(self, obj):
        accuracy = obj.accuracy
        color = 'green' if accuracy >= 80 else 'orange' if accuracy >= 60 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, accuracy
        )
    accuracy_percent.short_description = 'Accuracy'
    
    def avg_time_per_card(self, obj):
        return f"{obj.average_time_per_card:.1f}s"
    avg_time_per_card.short_description = 'Avg Time/Card'

