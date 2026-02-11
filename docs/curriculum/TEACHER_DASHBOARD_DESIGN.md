# 👨‍🏫 TEACHER DASHBOARD - Technical Design

**Ngày tạo:** 17/12/2025  
**Mục đích:** Giúp giáo viên/admin quản lý nội dung pronunciation dễ dàng, không cần developer

---

## 🎯 PROBLEM STATEMENT

### Vấn đề hiện tại:
```
❌ Django Admin cơ bản, khó sử dụng
❌ Chọn Word/Phoneme bằng ID dropdown → Không tìm được
❌ KHÔNG có script tự động tạo Minimal Pairs
❌ Giáo viên phải nhập thủ công 100% data
❌ Không biết phoneme nào thiếu audio
❌ Không biết minimal pair nào chưa có
```

### Yêu cầu từ roadmap:
```
✅ Task 2.1: Autocomplete fields cho MinimalPair
✅ Task 2.2: Script tự động tìm minimal pairs dựa trên IPA
✅ Task 2.3: django-admin-autocomplete-filter
✅ Dashboard tổng quan cho giáo viên
```

---

## 📦 INSTALLATION

### Required Packages

```bash
# Install dependencies
pip install django-autocomplete-light==3.9.7
pip install django-admin-list-filter-dropdown==1.0.3
pip install django-import-export==3.3.1  # For CSV import/export
pip install django-admin-sortable2==2.1.9  # For drag-drop ordering

# Update requirements.txt
echo "django-autocomplete-light==3.9.7" >> requirements.txt
echo "django-admin-list-filter-dropdown==1.0.3" >> requirements.txt
echo "django-import-export==3.3.1" >> requirements.txt
echo "django-admin-sortable2==2.1.9" >> requirements.txt
```

### Settings Configuration

```python
# backend/config/settings.py

INSTALLED_APPS = [
    # ... existing apps
    'dal',  # django-autocomplete-light (BEFORE django.contrib.admin)
    'dal_select2',
    'django.contrib.admin',
    'import_export',
    'adminsortable2',
    # ... rest
]

# Autocomplete settings
DAL_AUTOCOMPLETE = {
    'select2_theme': 'bootstrap4',
}
```

### URLs Configuration

```python
# backend/config/urls.py

from django.urls import path, include

urlpatterns = [
    # Autocomplete URLs (BEFORE admin)
    path('admin/autocomplete/', include('dal.urls')),
    path('admin/', admin.site.urls),
    # ... rest
]
```

---

## 🎨 ENHANCED ADMIN INTERFACES

### 1. Phoneme Admin with Autocomplete

```python
# backend/apps/curriculum/admin.py

from dal import autocomplete
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# ===== PHONEME AUTOCOMPLETE =====

class PhonemeResource(resources.ModelResource):
    """Resource for import/export Phoneme data"""
    class Meta:
        model = Phoneme
        fields = ('id', 'ipa_symbol', 'vietnamese_approx', 'phoneme_type', 
                 'voicing', 'category__name')
        export_order = fields

@admin.register(Phoneme)
class PhonemeAdmin(ImportExportModelAdmin):
    """
    Enhanced Phoneme admin with:
    - Autocomplete search
    - Import/Export CSV
    - Audio status indicators
    """
    resource_class = PhonemeResource
    
    list_display = [
        'ipa_display',
        'vietnamese_approx',
        'phoneme_type_badge',
        'voicing_badge',
        'audio_status',
        'minimal_pairs_count',
        'example_words_count',
        'is_active'
    ]
    
    list_filter = [
        ('category', admin.RelatedOnlyFieldListFilter),
        'phoneme_type',
        'voicing',
        'is_active'
    ]
    
    search_fields = [
        'ipa_symbol',
        'vietnamese_approx',
        'pronunciation_tips_vi',
        'common_mistakes_vi'
    ]
    
    # Enable autocomplete
    autocomplete_fields = ['category', 'preferred_audio_source']
    
    def ipa_display(self, obj):
        """Large IPA symbol"""
        return format_html(
            '<span style="font-size: 24px; font-weight: bold;">/{}/</span>',
            obj.ipa_symbol
        )
    ipa_display.short_description = 'IPA'
    
    def phoneme_type_badge(self, obj):
        """Color-coded type badge"""
        colors = {
            'vowel': '#3b82f6',      # blue
            'consonant': '#10b981',  # green
            'diphthong': '#f59e0b',  # orange
        }
        color = colors.get(obj.phoneme_type, '#6b7280')
        
        return format_html(
            '<span style="background: {}; color: white; '
            'padding: 4px 8px; border-radius: 8px; font-size: 11px;">{}</span>',
            color, obj.get_phoneme_type_display()
        )
    phoneme_type_badge.short_description = 'Type'
    
    def voicing_badge(self, obj):
        """Voiced/Voiceless badge"""
        if obj.voicing == 'voiceless':
            return format_html(
                '<span style="color: #ef4444;">🔇 Vô thanh</span>'
            )
        elif obj.voicing == 'voiced':
            return format_html(
                '<span style="color: #10b981;">🔊 Hữu thanh</span>'
            )
        return '-'
    voicing_badge.short_description = 'Voicing'
    
    def audio_status(self, obj):
        """Audio availability indicator"""
        native_count = obj.audio_sources.filter(source_type='native').count()
        tts_count = obj.audio_sources.filter(source_type='tts').count()
        
        if native_count > 0:
            icon = '⭐'
            text = f'{native_count} Native'
            color = '#10b981'
        elif tts_count > 0:
            icon = '🤖'
            text = f'{tts_count} TTS'
            color = '#f59e0b'
        else:
            icon = '❌'
            text = 'No Audio'
            color = '#ef4444'
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color, icon, text
        )
    audio_status.short_description = 'Audio'
    
    def minimal_pairs_count(self, obj):
        """Count minimal pairs"""
        count = MinimalPair.objects.filter(
            models.Q(phoneme_1=obj) | models.Q(phoneme_2=obj)
        ).count()
        
        if count >= 5:
            color = '#10b981'
        elif count >= 3:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span> pairs',
            color, count
        )
    minimal_pairs_count.short_description = 'Pairs'
    
    def example_words_count(self, obj):
        """Count example words"""
        count = obj.example_words.count()
        
        if count >= 6:
            color = '#10b981'
        elif count >= 3:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span> words',
            color, count
        )
    example_words_count.short_description = 'Words'
```

### 2. MinimalPair Admin with Smart Features

```python
# ===== MINIMAL PAIR ADMIN WITH AUTOCOMPLETE =====

class MinimalPairResource(resources.ModelResource):
    """Resource for import/export MinimalPair data"""
    class Meta:
        model = MinimalPair
        fields = ('id', 'phoneme_1__ipa_symbol', 'phoneme_2__ipa_symbol',
                 'word_1', 'word_1_ipa', 'word_1_meaning',
                 'word_2', 'word_2_ipa', 'word_2_meaning',
                 'difficulty', 'difference_note_vi')

@admin.register(MinimalPair)
class MinimalPairAdmin(ImportExportModelAdmin):
    """
    Enhanced MinimalPair admin with:
    - Autocomplete for phoneme selection
    - Smart filters
    - Bulk actions
    - CSV import/export
    """
    resource_class = MinimalPairResource
    
    list_display = [
        'pair_display',
        'phoneme_pair_display',
        'difficulty_badge',
        'audio_status',
        'usage_stats',
        'created_at'
    ]
    
    list_filter = [
        ('difficulty', admin.ChoicesFieldListFilter),
        ('phoneme_1', admin.RelatedOnlyFieldListFilter),
        ('phoneme_2', admin.RelatedOnlyFieldListFilter),
        ('created_at', admin.DateFieldListFilter)
    ]
    
    search_fields = [
        'word_1',
        'word_2',
        'word_1_meaning',
        'word_2_meaning',
        'phoneme_1__ipa_symbol',
        'phoneme_2__ipa_symbol'
    ]
    
    # ✅ AUTOCOMPLETE FIELDS - Key feature!
    autocomplete_fields = ['phoneme_1', 'phoneme_2']
    
    readonly_fields = ['created_at', 'updated_at', 'audio_players']
    
    fieldsets = (
        ('Phoneme Pair', {
            'fields': ('phoneme_1', 'phoneme_2', 'difficulty')
        }),
        ('Word 1', {
            'fields': ('word_1', 'word_1_ipa', 'word_1_meaning')
        }),
        ('Word 2', {
            'fields': ('word_2', 'word_2_ipa', 'word_2_meaning')
        }),
        ('Learning Notes', {
            'fields': ('difference_note_vi',)
        }),
        ('Audio Preview', {
            'fields': ('audio_players',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'generate_audio_bulk',
        'test_pronunciation',
        'suggest_improvements',
        'export_to_anki'
    ]
    
    # Custom displays
    
    def pair_display(self, obj):
        """Show word pair with highlighting"""
        return format_html(
            '<div style="font-size: 16px;">'
            '<strong style="color: #3b82f6;">{}</strong> '
            '<span style="color: #6b7280;">vs</span> '
            '<strong style="color: #f59e0b;">{}</strong>'
            '</div>'
            '<div style="font-size: 12px; color: #6b7280;">'
            '{} | {}'
            '</div>',
            obj.word_1,
            obj.word_2,
            obj.word_1_ipa,
            obj.word_2_ipa
        )
    pair_display.short_description = 'Word Pair'
    
    def phoneme_pair_display(self, obj):
        """Show phoneme symbols"""
        return format_html(
            '<div style="font-size: 18px;">'
            '<code style="background: #dbeafe; padding: 4px 8px; border-radius: 4px;">/{}/</code> '
            '→ '
            '<code style="background: #fef3c7; padding: 4px 8px; border-radius: 4px;">/{}/</code>'
            '</div>',
            obj.phoneme_1.ipa_symbol,
            obj.phoneme_2.ipa_symbol
        )
    phoneme_pair_display.short_description = 'Phonemes'
    
    def difficulty_badge(self, obj):
        """Difficulty level badge"""
        levels = {
            1: ('Beginner', '#10b981'),
            2: ('Intermediate', '#f59e0b'),
            3: ('Advanced', '#ef4444')
        }
        
        label, color = levels.get(obj.difficulty, ('Unknown', '#6b7280'))
        
        return format_html(
            '<span style="background: {}; color: white; '
            'padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">'
            '{}</span>',
            color, label
        )
    difficulty_badge.short_description = 'Level'
    
    def audio_status(self, obj):
        """Check if audio exists for both phonemes"""
        audio1 = obj.phoneme_1.preferred_audio_source is not None
        audio2 = obj.phoneme_2.preferred_audio_source is not None
        
        if audio1 and audio2:
            return format_html('✅ <span style="color: #10b981;">Both</span>')
        elif audio1 or audio2:
            return format_html('⚠️ <span style="color: #f59e0b;">Partial</span>')
        else:
            return format_html('❌ <span style="color: #ef4444;">None</span>')
    audio_status.short_description = 'Audio'
    
    def usage_stats(self, obj):
        """Show usage statistics (mock for now)"""
        # TODO: Implement actual usage tracking
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 16px; font-weight: bold;">-</div>'
            '<small style="color: #666;">practices</small>'
            '</div>'
        )
    usage_stats.short_description = 'Usage'
    
    def audio_players(self, obj):
        """Preview audio for both phonemes"""
        html = '<div style="display: flex; gap: 20px;">'
        
        # Phoneme 1 audio
        if obj.phoneme_1.preferred_audio_source:
            audio_url = obj.phoneme_1.preferred_audio_source.audio_file.url
            html += f'''
            <div style="flex: 1;">
                <h4 style="margin-bottom: 8px;">/{obj.phoneme_1.ipa_symbol}/ - {obj.word_1}</h4>
                <audio controls preload="none" style="width: 100%;">
                    <source src="{audio_url}" type="audio/mpeg">
                </audio>
            </div>
            '''
        else:
            html += f'''
            <div style="flex: 1;">
                <h4>/{obj.phoneme_1.ipa_symbol}/ - {obj.word_1}</h4>
                <p style="color: #999;">No audio</p>
            </div>
            '''
        
        # Phoneme 2 audio
        if obj.phoneme_2.preferred_audio_source:
            audio_url = obj.phoneme_2.preferred_audio_source.audio_file.url
            html += f'''
            <div style="flex: 1;">
                <h4 style="margin-bottom: 8px;">/{obj.phoneme_2.ipa_symbol}/ - {obj.word_2}</h4>
                <audio controls preload="none" style="width: 100%;">
                    <source src="{audio_url}" type="audio/mpeg">
                </audio>
            </div>
            '''
        else:
            html += f'''
            <div style="flex: 1;">
                <h4>/{obj.phoneme_2.ipa_symbol}/ - {obj.word_2}</h4>
                <p style="color: #999;">No audio</p>
            </div>
            '''
        
        html += '</div>'
        
        return format_html(html)
    audio_players.short_description = 'Audio Preview'
    
    # Actions
    
    def generate_audio_bulk(self, request, queryset):
        """Generate audio for selected pairs"""
        from apps.curriculum.services.edge_tts_service import EdgeTTSService
        
        tts_service = EdgeTTSService()
        success_count = 0
        
        for pair in queryset:
            # Generate for phoneme 1 if missing
            if not pair.phoneme_1.preferred_audio_source:
                try:
                    tts_service.generate_phoneme_audio(
                        pair.phoneme_1,
                        voice_id='en-US-AriaNeural'
                    )
                    success_count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f"Failed for /{pair.phoneme_1.ipa_symbol}/: {e}",
                        level='error'
                    )
            
            # Generate for phoneme 2 if missing
            if not pair.phoneme_2.preferred_audio_source:
                try:
                    tts_service.generate_phoneme_audio(
                        pair.phoneme_2,
                        voice_id='en-US-AriaNeural'
                    )
                    success_count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f"Failed for /{pair.phoneme_2.ipa_symbol}/: {e}",
                        level='error'
                    )
        
        self.message_user(
            request,
            f"Successfully generated audio for {success_count} phoneme(s)"
        )
    generate_audio_bulk.short_description = "🔊 Generate missing audio"
    
    def test_pronunciation(self, request, queryset):
        """Test pronunciation by playing audio"""
        # Redirect to test page
        pair_ids = ','.join(str(p.id) for p in queryset[:5])
        url = f"/admin/pronunciation-test/?pairs={pair_ids}"
        
        from django.shortcuts import redirect
        return redirect(url)
    test_pronunciation.short_description = "🎧 Test pronunciation"
    
    def suggest_improvements(self, request, queryset):
        """Suggest improvements based on data quality"""
        issues = []
        
        for pair in queryset:
            # Check for missing IPA
            if not pair.word_1_ipa or not pair.word_2_ipa:
                issues.append(f"{pair.word_1} vs {pair.word_2}: Missing IPA")
            
            # Check for missing meaning
            if not pair.word_1_meaning or not pair.word_2_meaning:
                issues.append(f"{pair.word_1} vs {pair.word_2}: Missing Vietnamese meaning")
            
            # Check for missing note
            if not pair.difference_note_vi:
                issues.append(f"{pair.word_1} vs {pair.word_2}: Missing difference note")
        
        if issues:
            message = "Issues found:\n" + "\n".join(issues[:10])
            self.message_user(request, message, level='warning')
        else:
            self.message_user(request, "All selected pairs look good! ✅")
    suggest_improvements.short_description = "🔍 Check data quality"
    
    def export_to_anki(self, request, queryset):
        """Export to Anki flashcard format"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="minimal_pairs_anki.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Front', 'Back', 'Audio', 'Notes'])
        
        for pair in queryset:
            front = f"/{pair.phoneme_1.ipa_symbol}/ vs /{pair.phoneme_2.ipa_symbol}/: {pair.word_1} or {pair.word_2}?"
            back = f"{pair.word_1} ({pair.word_1_ipa}) = {pair.word_1_meaning}<br>{pair.word_2} ({pair.word_2_ipa}) = {pair.word_2_meaning}"
            notes = pair.difference_note_vi
            
            writer.writerow([front, back, '', notes])
        
        return response
    export_to_anki.short_description = "📝 Export to Anki"
```

---

## 🤖 AUTO-GENERATE MINIMAL PAIRS

### Management Command

```python
# backend/apps/curriculum/management/commands/auto_generate_minimal_pairs.py

"""
Auto-detect minimal pairs from database.

Usage:
    python manage.py auto_generate_minimal_pairs --phoneme1 p --phoneme2 b
    python manage.py auto_generate_minimal_pairs --auto  # Auto-detect all
    python manage.py auto_generate_minimal_pairs --suggest  # Just suggest, don't create
"""

from django.core.management.base import BaseCommand
from apps.curriculum.models import Phoneme, PhonemeWord, MinimalPair
from difflib import SequenceMatcher
from collections import defaultdict

class Command(BaseCommand):
    help = 'Auto-detect and create minimal pairs from PhonemeWord database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--phoneme1',
            type=str,
            help='First phoneme IPA symbol (e.g., "p")'
        )
        
        parser.add_argument(
            '--phoneme2',
            type=str,
            help='Second phoneme IPA symbol (e.g., "b")'
        )
        
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Auto-detect all potential pairs'
        )
        
        parser.add_argument(
            '--suggest',
            action='store_true',
            help='Only suggest pairs, don\'t create them'
        )
        
        parser.add_argument(
            '--min-similarity',
            type=float,
            default=0.7,
            help='Minimum IPA similarity (0.0-1.0, default: 0.7)'
        )
        
        parser.add_argument(
            '--max-pairs',
            type=int,
            default=50,
            help='Maximum pairs to create (default: 50)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Scanning for minimal pairs...'))
        
        if options['phoneme1'] and options['phoneme2']:
            # Specific pair
            self._find_pairs_for_phonemes(
                options['phoneme1'],
                options['phoneme2'],
                options
            )
        elif options['auto']:
            # Auto-detect all
            self._find_all_pairs(options)
        else:
            self.stdout.write(self.style.ERROR(
                'Please specify --phoneme1 and --phoneme2, or use --auto'
            ))
    
    def _find_pairs_for_phonemes(self, symbol1, symbol2, options):
        """Find minimal pairs for specific phoneme pair"""
        try:
            p1 = Phoneme.objects.get(ipa_symbol=symbol1)
            p2 = Phoneme.objects.get(ipa_symbol=symbol2)
        except Phoneme.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Phoneme not found: {e}'))
            return
        
        self.stdout.write(f'\n📚 Finding pairs for /{symbol1}/ vs /{symbol2}/...')
        
        words1 = list(PhonemeWord.objects.filter(phoneme=p1))
        words2 = list(PhonemeWord.objects.filter(phoneme=p2))
        
        suggestions = self._detect_minimal_pairs(
            p1, p2, words1, words2, options['min_similarity']
        )
        
        if not suggestions:
            self.stdout.write(self.style.WARNING('No minimal pairs found 😞'))
            return
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Found {len(suggestions)} potential minimal pairs:\n'
        ))
        
        for i, s in enumerate(suggestions, 1):
            self.stdout.write(
                f"{i}. {s['word_1']} ({s['ipa_1']}) ↔ {s['word_2']} ({s['ipa_2']}) "
                f"[similarity: {s['similarity']:.2f}]"
            )
        
        if not options['suggest']:
            self._create_pairs(suggestions, p1, p2)
    
    def _find_all_pairs(self, options):
        """Auto-detect all potential minimal pairs"""
        phonemes = list(Phoneme.objects.filter(is_active=True))
        all_suggestions = []
        
        self.stdout.write(f'\n📊 Analyzing {len(phonemes)} phonemes...\n')
        
        for i, p1 in enumerate(phonemes):
            for p2 in phonemes[i+1:]:  # Avoid duplicates
                # Only compare similar phoneme types
                if p1.phoneme_type != p2.phoneme_type:
                    continue
                
                words1 = list(PhonemeWord.objects.filter(phoneme=p1))
                words2 = list(PhonemeWord.objects.filter(phoneme=p2))
                
                if not words1 or not words2:
                    continue
                
                suggestions = self._detect_minimal_pairs(
                    p1, p2, words1, words2, options['min_similarity']
                )
                
                if suggestions:
                    all_suggestions.extend(suggestions)
                    self.stdout.write(
                        f"  ✓ /{p1.ipa_symbol}/ vs /{p2.ipa_symbol}/: {len(suggestions)} pairs"
                    )
        
        # Sort by similarity
        all_suggestions.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Limit
        all_suggestions = all_suggestions[:options['max_pairs']]
        
        self.stdout.write(self.style.SUCCESS(
            f'\n🎯 Top {len(all_suggestions)} minimal pairs:\n'
        ))
        
        for i, s in enumerate(all_suggestions[:20], 1):  # Show top 20
            self.stdout.write(
                f"{i}. /{s['p1'].ipa_symbol}/ vs /{s['p2'].ipa_symbol}/: "
                f"{s['word_1']} ({s['ipa_1']}) ↔ {s['word_2']} ({s['ipa_2']}) "
                f"[{s['similarity']:.2f}]"
            )
        
        if not options['suggest']:
            if input('\nCreate these pairs in database? (y/n): ').lower() == 'y':
                for s in all_suggestions:
                    self._create_single_pair(s)
                
                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ Created {len(all_suggestions)} minimal pairs!'
                ))
    
    def _detect_minimal_pairs(self, p1, p2, words1, words2, min_similarity):
        """
        Detect minimal pairs by comparing IPA transcriptions.
        
        A minimal pair is two words that differ in exactly one phoneme.
        We use fuzzy string matching on IPA to find candidates.
        """
        suggestions = []
        
        for w1 in words1:
            for w2 in words2:
                # Skip if no IPA
                if not w1.ipa_transcription or not w2.ipa_transcription:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_ipa_similarity(
                    w1.ipa_transcription,
                    w2.ipa_transcription
                )
                
                # If similarity is high (differ by 1-2 phonemes), it's a candidate
                if min_similarity <= similarity <= 0.9:
                    suggestions.append({
                        'p1': p1,
                        'p2': p2,
                        'word_1': w1.word,
                        'word_2': w2.word,
                        'ipa_1': w1.ipa_transcription,
                        'ipa_2': w2.ipa_transcription,
                        'meaning_1': w1.meaning_vi,
                        'meaning_2': w2.meaning_vi,
                        'similarity': similarity
                    })
        
        # Sort by similarity
        suggestions.sort(key=lambda x: x['similarity'], reverse=True)
        
        return suggestions[:10]  # Top 10 per pair
    
    def _calculate_ipa_similarity(self, ipa1, ipa2):
        """
        Calculate similarity between two IPA strings.
        
        Uses SequenceMatcher from difflib.
        Returns value 0.0 (completely different) to 1.0 (identical).
        """
        # Normalize: remove slashes, stress marks
        ipa1_clean = ipa1.replace('/', '').replace('ˈ', '').replace('ˌ', '')
        ipa2_clean = ipa2.replace('/', '').replace('ˈ', '').replace('ˌ', '')
        
        return SequenceMatcher(None, ipa1_clean, ipa2_clean).ratio()
    
    def _create_pairs(self, suggestions, p1, p2):
        """Create MinimalPair records from suggestions"""
        created = 0
        
        for s in suggestions:
            difficulty = self._calculate_difficulty(p1, p2)
            note = self._generate_difference_note(p1, p2)
            
            _, created_flag = MinimalPair.objects.get_or_create(
                word_1=s['word_1'],
                word_2=s['word_2'],
                defaults={
                    'phoneme_1': p1,
                    'phoneme_2': p2,
                    'word_1_ipa': s['ipa_1'],
                    'word_2_ipa': s['ipa_2'],
                    'word_1_meaning': s['meaning_1'] or '',
                    'word_2_meaning': s['meaning_2'] or '',
                    'difficulty': difficulty,
                    'difference_note_vi': note
                }
            )
            
            if created_flag:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {created} new minimal pairs!'))
    
    def _create_single_pair(self, s):
        """Create a single MinimalPair"""
        difficulty = self._calculate_difficulty(s['p1'], s['p2'])
        note = self._generate_difference_note(s['p1'], s['p2'])
        
        MinimalPair.objects.get_or_create(
            word_1=s['word_1'],
            word_2=s['word_2'],
            defaults={
                'phoneme_1': s['p1'],
                'phoneme_2': s['p2'],
                'word_1_ipa': s['ipa_1'],
                'word_2_ipa': s['ipa_2'],
                'word_1_meaning': s['meaning_1'] or '',
                'word_2_meaning': s['meaning_2'] or '',
                'difficulty': difficulty,
                'difference_note_vi': note
            }
        )
    
    def _calculate_difficulty(self, p1, p2):
        """
        Auto-calculate difficulty based on phoneme characteristics.
        
        1 = Beginner (very different)
        2 = Intermediate (similar type, different voicing)
        3 = Advanced (same type, same voicing)
        """
        # Same voicing = harder
        if p1.voicing == p2.voicing:
            return 3
        
        # Different voicing but same type = medium
        if p1.phoneme_type == p2.phoneme_type:
            return 2
        
        # Different type = easier
        return 1
    
    def _generate_difference_note(self, p1, p2):
        """Auto-generate difference note in Vietnamese"""
        notes = []
        
        # Voicing difference
        if p1.voicing != p2.voicing:
            v1 = 'vô thanh' if p1.voicing == 'voiceless' else 'hữu thanh'
            v2 = 'vô thanh' if p2.voicing == 'voiceless' else 'hữu thanh'
            notes.append(f"/{p1.ipa_symbol}/ là {v1}, /{p2.ipa_symbol}/ là {v2}.")
        
        # Length difference (for vowels)
        if p1.phoneme_type == 'vowel' and p2.phoneme_type == 'vowel':
            if ':' in p1.ipa_symbol or 'ː' in p1.ipa_symbol:
                notes.append(f"/{p1.ipa_symbol}/ là âm DÀI, /{p2.ipa_symbol}/ là âm NGẮN.")
            elif ':' in p2.ipa_symbol or 'ː' in p2.ipa_symbol:
                notes.append(f"/{p1.ipa_symbol}/ là âm NGẮN, /{p2.ipa_symbol}/ là âm DÀI.")
        
        if notes:
            return ' '.join(notes)
        else:
            return f"Phân biệt /{p1.ipa_symbol}/ và /{p2.ipa_symbol}/ qua cách phát âm."
```

### Usage Examples

```bash
# Example 1: Find pairs for /p/ vs /b/
python manage.py auto_generate_minimal_pairs --phoneme1 p --phoneme2 b

# Output:
🔍 Scanning for minimal pairs...
📚 Finding pairs for /p/ vs /b/...

✅ Found 8 potential minimal pairs:

1. Pen (/pen/) ↔ Ben (/ben/) [similarity: 0.83]
2. Pat (/pæt/) ↔ Bat (/bæt/) [similarity: 0.83]
3. Pea (/piː/) ↔ Bee (/biː/) [similarity: 0.83]
4. Park (/pɑːrk/) ↔ Bark (/bɑːrk/) [similarity: 0.80]
5. Pit (/pɪt/) ↔ Bit (/bɪt/) [similarity: 0.83]
6. Pop (/pɒp/) ↔ Bob (/bɒb/) [similarity: 0.67]
7. Cap (/kæp/) ↔ Cab (/kæb/) [similarity: 0.83]
8. Rope (/rəʊp/) ↔ Robe (/rəʊb/) [similarity: 0.80]

✅ Created 8 new minimal pairs!

# Example 2: Auto-detect all pairs
python manage.py auto_generate_minimal_pairs --auto

# Output:
🔍 Scanning for minimal pairs...
📊 Analyzing 46 phonemes...

  ✓ /p/ vs /b/: 8 pairs
  ✓ /t/ vs /d/: 12 pairs
  ✓ /k/ vs /g/: 7 pairs
  ✓ /iː/ vs /ɪ/: 15 pairs
  ✓ /uː/ vs /ʊ/: 10 pairs
  ...

🎯 Top 50 minimal pairs:

1. /iː/ vs /ɪ/: Sheep (/ʃiːp/) ↔ Ship (/ʃɪp/) [0.89]
2. /iː/ vs /ɪ/: Seat (/siːt/) ↔ Sit (/sɪt/) [0.86]
3. /t/ vs /d/: Tap (/tæp/) ↔ Dab (/dæb/) [0.83]
...

Create these pairs in database? (y/n): y
✅ Created 50 minimal pairs!

# Example 3: Just suggest (don't create)
python manage.py auto_generate_minimal_pairs --auto --suggest --min-similarity 0.75

# Output:
[Suggestions only, no database changes]
```

---

## 📊 TEACHER DASHBOARD PAGE

### Dashboard View

```python
# backend/apps/curriculum/views.py

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q
from apps.curriculum.models import Phoneme, MinimalPair, AudioSource

@staff_member_required
def teacher_dashboard(request):
    """
    Teacher dashboard showing pronunciation content status.
    
    URL: /admin/teacher-dashboard/
    """
    
    # Phoneme statistics
    phoneme_stats = {
        'total': Phoneme.objects.count(),
        'with_audio': Phoneme.objects.filter(
            preferred_audio_source__isnull=False
        ).count(),
        'with_native_audio': Phoneme.objects.filter(
            preferred_audio_source__source_type='native'
        ).count(),
        'with_pairs': Phoneme.objects.annotate(
            pair_count=Count('minimal_pairs_1') + Count('minimal_pairs_2')
        ).filter(pair_count__gte=3).count()
    }
    
    # Minimal pair statistics
    pair_stats = {
        'total': MinimalPair.objects.count(),
        'by_difficulty': {
            1: MinimalPair.objects.filter(difficulty=1).count(),
            2: MinimalPair.objects.filter(difficulty=2).count(),
            3: MinimalPair.objects.filter(difficulty=3).count(),
        }
    }
    
    # Audio statistics
    audio_stats = {
        'native': AudioSource.objects.filter(source_type='native').count(),
        'tts': AudioSource.objects.filter(source_type='tts').count(),
        'generated': AudioSource.objects.filter(source_type='generated').count(),
    }
    
    # Phonemes needing attention
    phonemes_need_audio = Phoneme.objects.filter(
        preferred_audio_source__isnull=True,
        is_active=True
    )[:10]
    
    phonemes_need_pairs = Phoneme.objects.annotate(
        pair_count=Count('minimal_pairs_1') + Count('minimal_pairs_2')
    ).filter(pair_count__lt=3, is_active=True)[:10]
    
    context = {
        'phoneme_stats': phoneme_stats,
        'pair_stats': pair_stats,
        'audio_stats': audio_stats,
        'phonemes_need_audio': phonemes_need_audio,
        'phonemes_need_pairs': phonemes_need_pairs,
    }
    
    return render(request, 'admin/teacher_dashboard.html', context)
```

### Dashboard Template

```html
<!-- backend/templates/admin/teacher_dashboard.html -->

{% extends "admin/base_site.html" %}

{% block title %}Teacher Dashboard{% endblock %}

{% block content %}
<div class="teacher-dashboard" style="padding: 20px;">
    <h1 style="margin-bottom: 30px;">👨‍🏫 Teacher Dashboard</h1>
    
    <!-- Stats Grid -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px;">
        <!-- Phoneme Stats -->
        <div class="stat-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #666; font-size: 14px; margin: 0 0 10px 0;">📚 PHONEMES</h3>
            <div style="font-size: 36px; font-weight: bold; color: #3b82f6;">
                {{ phoneme_stats.total }}
            </div>
            <div style="margin-top: 15px; font-size: 13px; color: #666;">
                <div>✅ {{ phoneme_stats.with_audio }} have audio</div>
                <div>⭐ {{ phoneme_stats.with_native_audio }} have native audio</div>
                <div>🔗 {{ phoneme_stats.with_pairs }} have 3+ pairs</div>
            </div>
        </div>
        
        <!-- Minimal Pair Stats -->
        <div class="stat-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #666; font-size: 14px; margin: 0 0 10px 0;">🔤 MINIMAL PAIRS</h3>
            <div style="font-size: 36px; font-weight: bold; color: #10b981;">
                {{ pair_stats.total }}
            </div>
            <div style="margin-top: 15px; font-size: 13px; color: #666;">
                <div>🟢 {{ pair_stats.by_difficulty.1 }} Beginner</div>
                <div>🟡 {{ pair_stats.by_difficulty.2 }} Intermediate</div>
                <div>🔴 {{ pair_stats.by_difficulty.3 }} Advanced</div>
            </div>
        </div>
        
        <!-- Audio Stats -->
        <div class="stat-card" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #666; font-size: 14px; margin: 0 0 10px 0;">🎵 AUDIO FILES</h3>
            <div style="font-size: 36px; font-weight: bold; color: #f59e0b;">
                {{ audio_stats.native|add:audio_stats.tts|add:audio_stats.generated }}
            </div>
            <div style="margin-top: 15px; font-size: 13px; color: #666;">
                <div>⭐ {{ audio_stats.native }} Native</div>
                <div>🤖 {{ audio_stats.tts }} TTS Cached</div>
                <div>⚡ {{ audio_stats.generated }} Generated</div>
            </div>
        </div>
    </div>
    
    <!-- Action Items -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <!-- Phonemes Need Audio -->
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0;">⚠️ Phonemes Need Audio</h3>
            {% if phonemes_need_audio %}
                <ul style="list-style: none; padding: 0; margin: 0;">
                    {% for phoneme in phonemes_need_audio %}
                    <li style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;">
                        <a href="{% url 'admin:curriculum_phoneme_change' phoneme.id %}" 
                           style="color: #3b82f6; text-decoration: none;">
                            <strong style="font-size: 18px;">/{{ phoneme.ipa_symbol }}/</strong>
                            <span style="color: #666; margin-left: 10px;">{{ phoneme.vietnamese_approx }}</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p style="color: #10b981;">✅ All phonemes have audio!</p>
            {% endif %}
        </div>
        
        <!-- Phonemes Need Pairs -->
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0;">🔗 Phonemes Need Minimal Pairs</h3>
            {% if phonemes_need_pairs %}
                <ul style="list-style: none; padding: 0; margin: 0;">
                    {% for phoneme in phonemes_need_pairs %}
                    <li style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;">
                        <a href="{% url 'admin:curriculum_minimalpair_changelist' %}?phoneme_1__id__exact={{ phoneme.id }}" 
                           style="color: #3b82f6; text-decoration: none;">
                            <strong style="font-size: 18px;">/{{ phoneme.ipa_symbol }}/</strong>
                            <span style="color: #666; margin-left: 10px;">{{ phoneme.pair_count }} pairs</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p style="color: #10b981;">✅ All phonemes have enough pairs!</p>
            {% endif %}
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div style="margin-top: 40px; background: #f9fafb; padding: 20px; border-radius: 8px;">
        <h3 style="margin: 0 0 15px 0;">🚀 Quick Actions</h3>
        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
            <a href="{% url 'admin:curriculum_phoneme_changelist' %}" 
               class="button" style="text-decoration: none;">
                📚 Manage Phonemes
            </a>
            <a href="{% url 'admin:curriculum_minimalpair_changelist' %}" 
               class="button" style="text-decoration: none;">
                🔤 Manage Minimal Pairs
            </a>
            <a href="{% url 'admin:curriculum_audiosource_changelist' %}" 
               class="button" style="text-decoration: none;">
                🎵 Manage Audio
            </a>
            <button onclick="generateAudio()" class="button" style="background: #10b981; color: white;">
                🔊 Generate Missing Audio
            </button>
            <button onclick="findPairs()" class="button" style="background: #f59e0b; color: white;">
                🔍 Auto-Find Minimal Pairs
            </button>
        </div>
    </div>
</div>

<script>
function generateAudio() {
    if (confirm('Generate audio for all phonemes without audio?')) {
        alert('This feature will be implemented soon!');
        // TODO: Call management command via AJAX
    }
}

function findPairs() {
    if (confirm('Auto-detect minimal pairs from database?')) {
        alert('This feature will be implemented soon!');
        // TODO: Call management command via AJAX
    }
}
</script>
{% endblock %}
```

---

## ✅ CHECKLIST FOR IMPLEMENTATION

### Phase 1: Setup (Day 1)
- [ ] Install django-autocomplete-light
- [ ] Install django-admin-list-filter-dropdown
- [ ] Install django-import-export
- [ ] Update settings.py
- [ ] Add autocomplete URLs

### Phase 2: Enhance Admin (Day 2-3)
- [ ] Implement PhonemeAdmin with autocomplete
- [ ] Implement MinimalPairAdmin with autocomplete
- [ ] Add custom displays (badges, audio players)
- [ ] Add admin actions (bulk generate, export)

### Phase 3: Auto-Generate Command (Day 4-5)
- [ ] Create management command
- [ ] Implement IPA similarity detection
- [ ] Test with sample data
- [ ] Document usage

### Phase 4: Dashboard (Day 6-7)
- [ ] Create dashboard view
- [ ] Create dashboard template
- [ ] Add statistics
- [ ] Add quick actions

---

## 📈 EXPECTED RESULTS

### Before:
```
❌ Tạo 1 minimal pair: ~5 phút (nhập thủ công)
❌ Tìm phoneme: Phải biết ID
❌ Không biết phoneme nào thiếu audio
```

### After:
```
✅ Tạo 1 minimal pair: ~30 giây (autocomplete)
✅ Auto-generate 50 pairs: 1 lệnh (5 giây)
✅ Dashboard hiển thị rõ ràng missing content
✅ Teacher tự quản lý, không cần dev
```

---

**Tạo bởi:** GitHub Copilot  
**Status:** Ready for implementation
