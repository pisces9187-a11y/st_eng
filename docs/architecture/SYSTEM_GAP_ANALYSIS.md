# 📊 PHÂN TÍCH HỆ THỐNG PHÁT ÂM - GAP ANALYSIS

**Ngày tạo:** 17/12/2025  
**Mục tiêu:** So sánh hệ thống hiện tại với yêu cầu ban đầu và đề xuất cải thiện

---

## 🎯 TÓM TẮT EXECUTIVE

### ✅ ĐIỂM MẠNH HIỆN TẠI
1. **Lesson IPA Introduction** (`/pronunciation/lesson/ipa-introduction/`) - **XUẤT SẮC**
   - UI/UX sinh động, hấp dẫn
   - Giải thích chi tiết cơ chế vật lý (lưỡi, môi, thanh quản)
   - Ví dụ thực tế với từ vựng đầy đủ
   - Có tips cho người Việt ("Đặt tờ giấy", "Đặt ngón tay lên cổ họng")

2. **Audio System** - Có cơ sở hạ tầng tốt
   - Model `AudioSource` với 3 loại: native/tts/generated
   - Cache mechanism với `AudioCache`
   - Quality scoring (100%/90%/80%)

3. **Database Design** - Đầy đủ cho phoneme learning
   - Phoneme, PhonemeCategory, PhonemeWord
   - MinimalPair cho discrimination
   - PronunciationLesson structure

### ❌ VẤN ĐỀ NGHIÊM TRỌNG

#### 1. **THIẾU AUDIO VERSIONING SYSTEM** ⚠️ **CRITICAL**
**Vấn đề:**
```
- Không có cơ chế quản lý phiên bản audio theo thời gian
- Không thể "quay lại" sử dụng audio ngày 15/12
- Khi xóa/tạo lại audio, mất hết history
- Upload audio gốc (native) đè lên TTS không có backup
```

**Ảnh hưởng:**
- Admin không kiểm soát được chất lượng audio
- Không A/B test được giữa các phiên bản
- Rủi ro mất dữ liệu cao

#### 2. **THIẾU TEACHER DASHBOARD** ⚠️ **CRITICAL**
**Yêu cầu từ roadmap:**
```
Task 2.1: Django Admin với autocomplete_fields cho MinimalPair
Task 2.2: Script tự động tìm minimal pairs dựa trên IPA
Task 2.3: django-admin-autocomplete-filter
```

**Thực tế hiện tại:**
- ❌ Django Admin cơ bản, chỉ có list/edit form thông thường
- ❌ Không có autocomplete cho Word selection
- ❌ KHÔNG có script tự động tìm minimal pairs
- ❌ Giáo viên phải thủ công nhập từng pair

**Ví dụ cụ thể:**
```python
# Hiện tại: Admin cơ bản
class MinimalPairAdmin(admin.ModelAdmin):
    list_display = ['word_1', 'word_2', 'phoneme_1', 'phoneme_2']
    # Dropdown ID rất khó dùng khi có 1000+ từ

# Cần có:
class MinimalPairAdmin(admin.ModelAdmin):
    autocomplete_fields = ['phoneme_1', 'phoneme_2']
    search_fields = ['word_1', 'word_2']
    
    def get_queryset(self, request):
        # Gợi ý cặp tự động dựa trên IPA diff
```

#### 3. **DISCRIMINATION PAGE KÉM HƠN LESSON PAGE** 📉
**So sánh:**

| Tiêu chí | Lesson Page ✅ | Discrimination Page ❌ |
|----------|---------------|----------------------|
| **Giải thích cơ chế** | "Đặt tờ giấy", "Rung thanh quản" | Chỉ có quiz dry |
| **Visual cues** | Tongue position, mouth shape | Không có diagram |
| **Context** | "Điểm chung vs khác biệt" | Thiếu context |
| **Engagement** | Mẹo, lỗi thường gặp | Chỉ có câu hỏi |
| **Pedagogical value** | 9/10 | 5/10 |

**Ví dụ cụ thể:**

✅ **Lesson page `/pronunciation/lesson/ipa-introduction/`:**
```
Âm bật hơi /p/ và /b/

Điểm chung: Miệng làm động tác Y HỆT nhau

Điểm khác biệt:
• /p/: Đặt tờ giấy trước miệng → giấy bay!
     Đọc "pờ" KHÔNG có âm "ờ"
• /b/: Đặt 2 ngón tay lên cổ họng → Rung!
     Đọc "bờ" nhanh, dứt khoát

Lỗi người Việt: Phát âm /p/ quá nhẹ hoặc thêm âm "ờ"

[6 ví dụ từ: Pen, Soup, Pop, Apple, Pea, Stop]
```

❌ **Discrimination page `/pronunciation/discrimination/47/`:**
```
[Phát audio ngẫu nhiên]
Chọn từ bạn nghe được:
○ Ship
○ Sheep

[Không có giải thích tại sao]
[Không có tips]
```

---

## 🔍 PHÂN TÍCH CHI TIẾT

### A. AUDIO MANAGEMENT - GAP ANALYSIS

#### ✅ Có sẵn (Current State)
```python
# backend/apps/curriculum/models.py

class AudioSource(models.Model):
    phoneme = ForeignKey(Phoneme)
    source_type = CharField(choices=['native', 'tts', 'generated'])
    audio_file = FileField(upload_to='phonemes/audio/%Y/%m/%d/')
    voice_id = CharField(default='en-US-AriaNeural')
    cached_until = DateTimeField()  # Cache expiry
    metadata = JSONField()
    
    def is_native(self):
        return self.source_type == 'native'
    
    def get_quality_score(self):
        return 100 if self.source_type == 'native' else 90
```

**Vấn đề:**
1. Upload path `%Y/%m/%d/` tạo folder theo ngày nhưng **không track version**
2. Không có field `version_number` hay `effective_date`
3. Không có relationship `previous_version`
4. `cached_until` chỉ cho TTS, không phải versioning

#### ❌ Thiếu (Missing Requirements)
```python
# CẦN BỔ SUNG:

class AudioVersion(models.Model):
    """Track all audio versions over time"""
    phoneme = ForeignKey(Phoneme)
    audio_source = ForeignKey(AudioSource)
    
    version_number = IntegerField()  # 1, 2, 3...
    effective_from = DateField()     # Ngày bắt đầu dùng
    effective_until = DateField(null=True)  # Ngày ngừng dùng
    
    is_active = BooleanField(default=False)  # Chỉ 1 version active
    
    # Metadata cho versioning
    uploaded_by = ForeignKey(User)
    upload_date = DateTimeField(auto_now_add=True)
    change_reason = TextField()  # "Giọng rõ hơn", "Fix quality"
    
    # A/B Testing
    usage_count = IntegerField(default=0)
    avg_user_rating = FloatField(null=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = [['phoneme', 'version_number']]
    
    def activate(self):
        """Set this version as active, deactivate others"""
        AudioVersion.objects.filter(
            phoneme=self.phoneme,
            is_active=True
        ).update(is_active=False, effective_until=timezone.now())
        
        self.is_active = True
        self.effective_from = timezone.now()
        self.save()

# Admin action để quay lại version cũ
class AudioVersionAdmin(admin.ModelAdmin):
    list_display = ['phoneme', 'version_number', 'effective_from', 
                   'is_active', 'quality_badge']
    actions = ['activate_version', 'compare_versions']
    
    def activate_version(self, request, queryset):
        """Activate selected version"""
        for version in queryset:
            version.activate()
            self.message_user(request, 
                f"Activated version {version.version_number}")
```

**Use Case cụ thể:**
```python
# Ngày 15/12: Upload native audio
v1 = AudioVersion.objects.create(
    phoneme=phoneme_p,
    audio_source=native_audio_1,
    version_number=1,
    effective_from='2025-12-15',
    change_reason="Initial native upload"
)
v1.activate()

# Ngày 17/12: Tạo TTS mới
v2 = AudioVersion.objects.create(
    phoneme=phoneme_p,
    audio_source=tts_audio_2,
    version_number=2,
    change_reason="Test TTS quality"
)
v2.activate()  # v1 tự động deactivate

# Ngày 18/12: Quay lại v1 vì v2 không tốt
v1.activate()  # v2 tự động deactivate

# View history
AudioVersion.objects.filter(phoneme=phoneme_p).order_by('-version_number')
# => [v2 (inactive), v1 (active)]
```

---

### B. TEACHER DASHBOARD - GAP ANALYSIS

#### ❌ Hiện trạng (Current State)
```python
# backend/apps/curriculum/admin.py - Line 400+

@admin.register(MinimalPair)
class MinimalPairAdmin(admin.ModelAdmin):
    list_display = ['word_1', 'word_2', 'phoneme_1', 'phoneme_2']
    list_filter = ['phoneme_1', 'difficulty']
    search_fields = ['word_1', 'word_2']
    
    # Vấn đề: raw_id_fields rất khó dùng
    raw_id_fields = ['phoneme_1', 'phoneme_2']
```

**Vấn đề:**
1. Chọn phoneme bằng ID popup → khó tìm
2. Không có gợi ý cặp tự động
3. Phải nhập thủ công 100% data

#### ✅ Cần có (Required Implementation)

##### Task 2.1: Autocomplete Fields
```python
# Cài đặt
pip install django-autocomplete-light

# backend/apps/curriculum/admin.py
from dal import autocomplete

@admin.register(Phoneme)
class PhonemeAdmin(admin.ModelAdmin):
    search_fields = ['ipa_symbol', 'vietnamese_approx']

@admin.register(MinimalPair)
class MinimalPairAdmin(admin.ModelAdmin):
    # ✅ Thay raw_id_fields bằng autocomplete
    autocomplete_fields = ['phoneme_1', 'phoneme_2']
    
    list_display = [
        'word_pair_display',    # "Ship vs Sheep"
        'phoneme_pair_display',  # "/ɪ/ vs /iː/"
        'difficulty_badge',
        'has_audio',
        'usage_count'
    ]
    
    list_filter = [
        'difficulty',
        ('phoneme_1', admin.RelatedOnlyFieldListFilter),
        'created_at'
    ]
    
    search_fields = [
        'word_1', 'word_2',
        'phoneme_1__ipa_symbol',
        'phoneme_2__ipa_symbol'
    ]
    
    actions = ['generate_audio_batch', 'test_pronunciation']
    
    def word_pair_display(self, obj):
        return format_html(
            '<strong>{}</strong> vs <strong>{}</strong>',
            obj.word_1, obj.word_2
        )
    word_pair_display.short_description = 'Word Pair'
    
    def phoneme_pair_display(self, obj):
        return format_html(
            '<code>/{}/</code> → <code>/{}/</code>',
            obj.phoneme_1.ipa_symbol,
            obj.phoneme_2.ipa_symbol
        )
    phoneme_pair_display.short_description = 'Phonemes'
```

##### Task 2.2: Auto-Generate Minimal Pairs
```python
# backend/apps/curriculum/management/commands/auto_generate_minimal_pairs.py

from django.core.management.base import BaseCommand
from apps.curriculum.models import Phoneme, PhonemeWord, MinimalPair
from difflib import SequenceMatcher

class Command(BaseCommand):
    help = 'Auto-detect minimal pairs from PhonemeWord database'
    
    def handle(self, *args, **options):
        self.stdout.write('🔍 Scanning for minimal pairs...')
        
        # Get all phoneme combinations
        phonemes = Phoneme.objects.all()
        suggestions = []
        
        for p1 in phonemes:
            for p2 in phonemes:
                if p1.id >= p2.id:  # Avoid duplicates
                    continue
                
                # Get words for each phoneme
                words_p1 = PhonemeWord.objects.filter(phoneme=p1)
                words_p2 = PhonemeWord.objects.filter(phoneme=p2)
                
                # Find minimal pairs (words differing in 1 phoneme only)
                for w1 in words_p1:
                    for w2 in words_p2:
                        similarity = self.calculate_similarity(
                            w1.ipa_transcription,
                            w2.ipa_transcription
                        )
                        
                        # If IPA differs by exactly 1 phoneme
                        if 0.7 <= similarity <= 0.9:
                            suggestions.append({
                                'p1': p1,
                                'p2': p2,
                                'word_1': w1.word,
                                'word_2': w2.word,
                                'ipa_1': w1.ipa_transcription,
                                'ipa_2': w2.ipa_transcription,
                                'similarity': similarity
                            })
        
        # Sort by similarity
        suggestions.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Print suggestions
        self.stdout.write(f'\n✅ Found {len(suggestions)} potential minimal pairs:\n')
        
        for i, s in enumerate(suggestions[:20], 1):  # Top 20
            self.stdout.write(
                f"{i}. /{s['p1'].ipa_symbol}/ vs /{s['p2'].ipa_symbol}/: "
                f"{s['word_1']} ({s['ipa_1']}) ↔ {s['word_2']} ({s['ipa_2']}) "
                f"[{s['similarity']:.2f}]"
            )
        
        # Ask to create
        if input('\nCreate these pairs in database? (y/n): ') == 'y':
            for s in suggestions[:20]:
                MinimalPair.objects.get_or_create(
                    word_1=s['word_1'],
                    word_2=s['word_2'],
                    defaults={
                        'phoneme_1': s['p1'],
                        'phoneme_2': s['p2'],
                        'word_1_ipa': s['ipa_1'],
                        'word_2_ipa': s['ipa_2'],
                        'difficulty': self.calculate_difficulty(s['p1'], s['p2'])
                    }
                )
            self.stdout.write(self.style.SUCCESS('✅ Created minimal pairs!'))
    
    def calculate_similarity(self, ipa1, ipa2):
        """Calculate IPA similarity (0.0 - 1.0)"""
        return SequenceMatcher(None, ipa1, ipa2).ratio()
    
    def calculate_difficulty(self, p1, p2):
        """Auto-calculate difficulty based on phoneme types"""
        # Same voicing = easier
        if p1.voicing == p2.voicing:
            return 3
        # Different voicing = medium
        elif p1.phoneme_type == p2.phoneme_type:
            return 2
        # Different type = hard
        else:
            return 1
```

**Chạy:**
```bash
python manage.py auto_generate_minimal_pairs

# Output:
🔍 Scanning for minimal pairs...

✅ Found 87 potential minimal pairs:

1. /ɪ/ vs /iː/: Ship (/ʃɪp/) ↔ Sheep (/ʃiːp/) [0.83]
2. /p/ vs /b/: Pen (/pen/) ↔ Ben (/ben/) [0.80]
3. /æ/ vs /e/: Bat (/bæt/) ↔ Bet (/bet/) [0.78]
...

Create these pairs in database? (y/n): y
✅ Created minimal pairs!
```

##### Task 2.3: Enhanced Filters
```python
# Install
pip install django-admin-list-filter-dropdown

# Usage
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, RelatedDropdownFilter
)

class MinimalPairAdmin(admin.ModelAdmin):
    list_filter = [
        ('difficulty', DropdownFilter),
        ('phoneme_1', RelatedDropdownFilter),
        ('phoneme_2', RelatedDropdownFilter),
        ('created_at', admin.DateFieldListFilter)
    ]
```

---

### C. DISCRIMINATION VS LESSON PAGE - UX ANALYSIS

#### 📊 Comparative Evaluation

| Feature | Lesson Page | Discrimination Page | Gap |
|---------|-------------|---------------------|-----|
| **Learning Objectives** | ✅ Rõ ràng | ❌ Không có | 🔴 Critical |
| **Physical Mechanism** | ✅ Tongue/lips diagram | ❌ Không có | 🔴 Critical |
| **Pronunciation Tips** | ✅ "Đặt tờ giấy" | ❌ Không có | 🟠 High |
| **Common Mistakes** | ✅ "Lỗi người Việt" | ❌ Không có | 🟠 High |
| **Context Before Quiz** | ✅ Giải thích trước | ❌ Vào quiz luôn | 🟠 High |
| **Visual Feedback** | ✅ Waveform (plan) | ❌ Chỉ text | 🟡 Medium |
| **Example Words** | ✅ 6 từ với IPA | ✅ Có trong quiz | ✅ OK |
| **Audio Quality** | ✅ TTS + native | ✅ TTS + native | ✅ OK |

#### ✅ Đề xuất cải tiến Discrimination Page

```html
<!-- backend/templates/pages/pronunciation_discrimination.html -->

<div id="discrimination-app">
    <!-- PHASE 1: Learning Context (NEW) -->
    <div v-if="phase === 'context'" class="context-section">
        <h2>📚 Trước khi luyện tập</h2>
        
        <div class="phoneme-comparison">
            <div class="phoneme-card">
                <h3>/[[ phoneme1.ipa_symbol ]]/</h3>
                <p class="vietnamese">[[ phoneme1.vietnamese_approx ]]</p>
                
                <!-- Physical mechanism -->
                <div class="mechanism">
                    <strong>Cách phát âm:</strong>
                    <p>[[ phoneme1.pronunciation_tips_vi ]]</p>
                </div>
                
                <!-- Diagram -->
                <img :src="phoneme1.mouth_diagram_url" alt="Mouth position">
            </div>
            
            <div class="vs-divider">VS</div>
            
            <div class="phoneme-card">
                <h3>/[[ phoneme2.ipa_symbol ]]/</h3>
                <p class="vietnamese">[[ phoneme2.vietnamese_approx ]]</p>
                
                <div class="mechanism">
                    <strong>Cách phát âm:</strong>
                    <p>[[ phoneme2.pronunciation_tips_vi ]]</p>
                </div>
                
                <img :src="phoneme2.mouth_diagram_url" alt="Mouth position">
            </div>
        </div>
        
        <!-- Key Differences -->
        <div class="key-differences alert alert-warning">
            <h4>🔑 Điểm khác biệt chính:</h4>
            <ul>
                <li v-for="diff in keyDifferences" :key="diff">
                    [[ diff ]]
                </li>
            </ul>
        </div>
        
        <!-- Common Mistakes -->
        <div class="common-mistakes alert alert-danger">
            <h4>⚠️ Lỗi người Việt hay mắc:</h4>
            <p>[[ phoneme1.common_mistakes_vi ]]</p>
        </div>
        
        <button @click="phase = 'quiz'" class="btn btn-primary btn-lg">
            Bắt đầu luyện tập →
        </button>
    </div>
    
    <!-- PHASE 2: Quiz (EXISTING - Enhanced) -->
    <div v-if="phase === 'quiz'" class="quiz-section">
        <!-- Add "Back to Context" button -->
        <button @click="phase = 'context'" class="btn btn-sm btn-outline-secondary">
            ← Xem lại giải thích
        </button>
        
        <!-- Existing quiz UI -->
        <div class="quiz-question">
            <h3>Câu [[ currentQuestion ]]/10</h3>
            <p>Bạn nghe thấy từ nào?</p>
            
            <!-- Audio player -->
            <audio ref="audioPlayer" @ended="audioPlayed = true"></audio>
            <button @click="playAudio()" class="btn-play">
                🔊 Phát audio
            </button>
            
            <!-- Options -->
            <div class="options">
                <button 
                    v-for="option in currentOptions" 
                    :key="option.word"
                    @click="selectAnswer(option)"
                    class="option-btn"
                    :class="{ selected: selectedAnswer === option }"
                >
                    <strong>[[ option.word ]]</strong>
                    <span class="ipa">[[ option.ipa ]]</span>
                    <span class="meaning">[[ option.meaning_vi ]]</span>
                </button>
            </div>
            
            <!-- Feedback (after answer) -->
            <div v-if="showFeedback" class="feedback" :class="{ correct: isCorrect }">
                <h4>[[ isCorrect ? '✅ Chính xác!' : '❌ Chưa đúng' ]]</h4>
                
                <!-- Show mechanism again -->
                <div class="feedback-explanation">
                    <p><strong>Từ đúng:</strong> [[ correctAnswer.word ]]</p>
                    <p><strong>Âm vị:</strong> /[[ correctAnswer.phoneme ]]/</p>
                    <p><strong>Lý do:</strong> [[ correctAnswer.tip ]]</p>
                </div>
                
                <button @click="nextQuestion()" class="btn btn-success">
                    Câu tiếp theo →
                </button>
            </div>
        </div>
    </div>
    
    <!-- PHASE 3: Results (EXISTING) -->
    <div v-if="phase === 'results'" class="results-section">
        <!-- Existing results UI -->
    </div>
</div>

<script>
new Vue({
    el: '#discrimination-app',
    delimiters: ['[[', ']]'],
    data: {
        phase: 'context',  // context → quiz → results
        phoneme1: {{ phoneme1_json|safe }},
        phoneme2: {{ phoneme2_json|safe }},
        keyDifferences: [
            'Cả hai đều mím môi nhưng /p/ KHÔNG rung thanh quản, /b/ CÓ rung',
            'Đặt ngón tay lên cổ họng: /b/ sẽ rung, /p/ không rung',
            '/p/ bật hơi mạnh hơn - tờ giấy bay xa hơn'
        ],
        currentQuestion: 1,
        // ... rest of quiz logic
    }
})
</script>
```

**Kết quả:**
- User thấy context TRƯỚC khi vào quiz
- Hiểu "tại sao" hai âm khác nhau
- Có thể quay lại xem giải thích bất cứ lúc nào
- Feedback sau mỗi câu có giải thích chi tiết

---

## 🎯 ROADMAP IMPLEMENTATION

### Phase 1: Audio Versioning (1 tuần)
**Priority:** 🔴 Critical

**Tasks:**
1. Tạo model `AudioVersion`
2. Migrate existing AudioSource → AudioVersion
3. Admin interface với actions:
   - View version history
   - Activate version
   - Compare versions (side-by-side audio player)
4. API endpoint: `GET /api/audio-versions/{phoneme_id}/`

**Deliverables:**
```python
# Usage example
phoneme = Phoneme.objects.get(ipa_symbol='p')
versions = phoneme.audio_versions.all()
# [v3 (active), v2 (inactive), v1 (inactive)]

# Activate old version
v1 = versions.get(version_number=1)
v1.activate()  # Now v1 is active, v3 is inactive
```

---

### Phase 2: Teacher Dashboard (1.5 tuần)
**Priority:** 🔴 Critical

**Tasks:**
1. **Week 1:**
   - Install django-autocomplete-light
   - Implement autocomplete_fields
   - Enhance MinimalPairAdmin UI
   
2. **Week 2:**
   - Create `auto_generate_minimal_pairs` command
   - Add admin actions (bulk audio generation)
   - Create teacher dashboard page (`/admin/dashboard/`)

**Deliverables:**
- ✅ Autocomplete cho phoneme selection
- ✅ Script tự động gợi ý minimal pairs
- ✅ Dashboard hiển thị:
  - Phoneme coverage (có bao nhiêu phoneme đã có audio)
  - Minimal pair coverage
  - Audio quality metrics

---

### Phase 3: Discrimination Page Redesign (1 tuần)
**Priority:** 🟠 High

**Tasks:**
1. Add "Context Phase" trước quiz
2. Display phoneme comparison (tongue/mouth diagrams)
3. Show key differences
4. Enhanced feedback with explanations
5. "Back to Context" button trong quiz

**Deliverables:**
- User journey: Context → Quiz → Results
- Pedagogically sound (theory before practice)
- Consistent với Lesson page style

---

### Phase 4: Audio Quality Dashboard (0.5 tuần)
**Priority:** 🟡 Medium

**Tasks:**
1. Create `/admin/audio-quality/` page
2. Show metrics:
   - Audio duration distribution
   - Quality score distribution
   - Native vs TTS ratio
   - Cache hit rate
3. Identify phonemes needing better audio

---

## 📈 SUCCESS METRICS

### Immediate (After Phase 1-2)
- ✅ Admin có thể quay lại audio cũ trong 2 clicks
- ✅ Tạo minimal pair mất <30s (vs 5 phút hiện tại)
- ✅ 100% phoneme có ít nhất 3 minimal pairs

### Medium-term (After Phase 3)
- ✅ User engagement tăng 30% trên discrimination page
- ✅ Quiz completion rate tăng từ 60% → 80%
- ✅ User hiểu "tại sao" (theo survey)

### Long-term
- ✅ Teacher có thể tự quản lý content không cần dev
- ✅ Audio versioning giúp A/B test
- ✅ Hệ thống scale lên 1000+ phoneme pairs

---

## 🔗 REFERENCES

- [Original Roadmap](untitled:Untitled-1)
- [Current Implementation](IMPLEMENTATION_COMPLETE.md)
- [Django Autocomplete Light Docs](https://django-autocomplete-light.readthedocs.io/)
- [Audio Management Best Practices](HUONG_DAN_TICH_HOP.md)

---

**Tạo bởi:** GitHub Copilot  
**Reviewed by:** [Cần review từ Product Owner]
