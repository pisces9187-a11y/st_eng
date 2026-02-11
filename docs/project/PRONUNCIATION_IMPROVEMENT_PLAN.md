# 🎯 KẾ HOẠCH CẢI THIỆN HỆ THỐNG PHÁT ÂM

## 📊 TỔNG QUAN

Tài liệu này chi tiết hóa kế hoạch nâng cấp hệ thống phát âm theo phương pháp chuẩn IPA, dựa trên:
- Phân tích khoảng trống (Gap Analysis)
- Phương pháp giảng dạy 4 giai đoạn
- Lỗi đặc thù người Việt

---

## 🔍 HIỆN TRẠNG

### ✅ ĐÃ CÓ
- Models: Phoneme, PhonemeCategory, MinimalPair, PronunciationLesson, TongueTwister
- Progress tracking: UserPronunciationProgress, UserPhonemeProgress, UserPronunciationStreak
- Discrimination system: DiscriminationSession, DiscriminationAttempt
- Audio management: AudioSource, AudioCache, AudioVersion
- Templates: discovery, learning, discrimination, production, library
- API endpoints đầy đủ

### ❌ THIẾU
- Dữ liệu: Database trống (0 phoneme categories, 0 lessons, 0 pairs)
- Cấu trúc: Không có CurriculumStage model
- Nội dung: Chưa có bài học Ending Sounds, Consonant Clusters, lỗi người Việt
- Tính năng: Scoring mock, chưa có so sánh âm Anh-Việt trực quan

---

## 📋 ROADMAP CẢI THIỆN

### **PHASE 1: XÂY DỰNG NỀN TẢNG DỮ LIỆU** ⭐ Ưu tiên cao

#### Task 1.1: Tạo Model CurriculumStage
**Mục tiêu:** Nhóm bài học theo 4 giai đoạn chuẩn

```python
class CurriculumStage(models.Model):
    """
    4 giai đoạn học phát âm:
    - Stage 1: Nguyên âm đơn (Monophthongs)
    - Stage 2: Phụ âm theo cặp (Consonant Pairs)
    - Stage 3: Nguyên âm đôi (Diphthongs)
    - Stage 4: Nâng cao (Clusters, Endings, Mistakes)
    """
    number = models.PositiveSmallIntegerField(unique=True)  # 1-4
    name = models.CharField(max_length=100)
    name_vi = models.CharField(max_length=100)
    description = models.TextField()
    description_vi = models.TextField()
    icon = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    
    # Yêu cầu để mở khóa giai đoạn này
    required_previous_stages = models.ManyToManyField('self', blank=True)
```

**File cần tạo:**
- `backend/apps/curriculum/models.py` - Thêm CurriculumStage
- `backend/apps/curriculum/migrations/` - Migration file

---

#### Task 1.2: Cập nhật PronunciationLesson Model
**Thêm field `stage`:**

```python
class PronunciationLesson(models.Model):
    # ... existing fields ...
    
    stage = models.ForeignKey(
        CurriculumStage,
        on_delete=models.PROTECT,
        related_name='lessons',
        verbose_name='Giai đoạn',
        null=True  # Temporary for migration
    )
    
    # Metadata ordering
    class Meta:
        ordering = ['stage__order', 'part_number', 'unit_number']
```

---

#### Task 1.3: Seed Dữ liệu Phoneme Categories & Phonemes
**Chạy management command:**

```bash
python manage.py seed_phonemes
```

**Nội dung seed (44 phonemes theo chuẩn IPA):**

**Nguyên âm đơn (12):**
- Short: /ɪ/ /e/ /æ/ /ʌ/ /ɒ/ /ʊ/ /ə/
- Long: /iː/ /ɑː/ /ɔː/ /uː/ /ɜː/

**Nguyên âm đôi (8):**
- /eɪ/ /aɪ/ /ɔɪ/ /aʊ/ /əʊ/ /ɪə/ /eə/ /ʊə/

**Phụ âm (24):**
- Plosives: /p/ /b/ /t/ /d/ /k/ /g/
- Fricatives: /f/ /v/ /θ/ /ð/ /s/ /z/ /ʃ/ /ʒ/ /h/
- Affricates: /tʃ/ /dʒ/
- Nasals: /m/ /n/ /ŋ/
- Approximants: /l/ /r/ /w/ /j/

**File cần tạo/sửa:**
- `backend/apps/curriculum/management/commands/seed_phonemes.py` - Đã có, cần review
- Add Vietnamese mistakes cho từng phoneme

---

#### Task 1.4: Tạo 15 Bài học Pronunciation theo 4 Giai đoạn

**Giai đoạn 1: Nguyên âm đơn (4 bài)**
1. Bài 1: Nguyên âm ngắn /ɪ/ /æ/ /ə/
2. Bài 2: Nguyên âm ngắn /ɒ/ /ʊ/ /e/
3. Bài 3: Nguyên âm dài /iː/ /ɑː/
4. Bài 4: Nguyên âm dài /uː/ /ɔː/ /ɜː/

**Giai đoạn 2: Phụ âm theo cặp (6 bài)**
5. Bài 5: /p/ - /b/ (môi - môi)
6. Bài 6: /t/ - /d/ (đầu lưỡi - răng)
7. Bài 7: /k/ - /g/ (cuống lưỡi)
8. Bài 8: /s/ - /z/ (âm xì)
9. Bài 9: /ʃ/ - /ʒ/ (cong môi)
10. Bài 10: /tʃ/ - /dʒ/ (bật hơi)

**Giai đoạn 3: Nguyên âm đôi (2 bài)**
11. Bài 11: /aɪ/ /eɪ/ /ɔɪ/
12. Bài 12: /aʊ/ /əʊ/

**Giai đoạn 4: Nâng cao (3 bài)**
13. Bài 13: Ending Sounds (Âm cuối)
14. Bài 14: Consonant Clusters (spring, street, plane)
15. Bài 15: Common Mistakes (R/D, N/L, /j/)

**File cần tạo:**
- `backend/apps/curriculum/management/commands/populate_curriculum_stages.py` - NEW
- Update `seed_pronunciation_lessons.py` với stage mapping

---

#### Task 1.5: Seed Minimal Pairs (Cặp tối thiểu)
**Ít nhất 100 cặp**, ví dụ:

| Phoneme 1 | Phoneme 2 | Word 1 | Word 2 | Difficulty |
|-----------|-----------|--------|--------|------------|
| /iː/ | /ɪ/ | sheep | ship | 1 |
| /p/ | /b/ | pin | bin | 1 |
| /s/ | /z/ | bus | buzz | 2 |
| /l/ | /r/ | light | right | 3 |
| /θ/ | /s/ | think | sink | 3 |

**File cần tạo:**
- `backend/apps/curriculum/management/commands/seed_minimal_pairs.py` - NEW
- CSV data: `backend/data/minimal_pairs.csv`

---

### **PHASE 2: CẢI THIỆN CURRICULUM FLOW** ⭐ Ưu tiên trung bình

#### Task 2.1: Refactor Library View
**Thay đổi từ:**
```
Hiển thị theo loại:
- Nguyên âm
- Phụ âm
- Nguyên âm đôi
```

**Thành:**
```
Hiển thị theo Giai đoạn:
├── 🎯 Giai đoạn 1: Nguyên âm đơn (4 bài)
├── 🔥 Giai đoạn 2: Phụ âm theo cặp (6 bài)
├── 🌊 Giai đoạn 3: Nguyên âm đôi (2 bài)
└── 🚀 Giai đoạn 4: Nâng cao (3 bài)
```

**File cần sửa:**
- `backend/apps/curriculum/template_views.py` - Update PronunciationLibraryView
- `backend/templates/curriculum/pronunciation/library.html` - Redesign layout

---

#### Task 2.2: Implement Prerequisites Logic
**Khi user vào lesson:**
```python
def can_access_lesson(user, lesson):
    """Check if user completed prerequisites"""
    for prereq in lesson.prerequisites.all():
        progress = UserPronunciationLessonProgress.objects.filter(
            user=user, 
            lesson=prereq,
            completed=True
        )
        if not progress.exists():
            return False
    return True
```

**File cần sửa:**
- `backend/apps/curriculum/views_pronunciation.py` - Add permission check
- `backend/templates/curriculum/pronunciation/library.html` - Show lock icon

---

#### Task 2.3: Dashboard Pronunciation Card
**Thêm card hiển thị:**
- Current stage (Giai đoạn hiện tại)
- Progress in stage (3/4 lessons completed)
- Next lesson to unlock
- Quick start button

**File cần sửa:**
- `backend/templates/users/dashboard.html` - Add pronunciation stats card

---

### **PHASE 3: BỔ SUNG NỘI DUNG ĐẶC THÙ NGƯỜI VIỆT** ⭐ Ưu tiên trung bình

#### Task 3.1: Thêm Field "Vietnamese Comparison"
**Cập nhật Phoneme model:**

```python
class Phoneme(models.Model):
    # ... existing fields ...
    
    vietnamese_comparison = models.TextField(
        blank=True,
        verbose_name='So sánh với tiếng Việt',
        help_text='Ví dụ: /p/ tiếng Anh bật hơi mạnh hơn /p/ tiếng Việt'
    )
    
    vietnamese_mistake_audio = models.FileField(
        upload_to='phonemes/mistake_audio/',
        blank=True,
        null=True,
        verbose_name='Audio lỗi người Việt hay mắc'
    )
```

**Migration:**
```bash
python manage.py makemigrations curriculum
python manage.py migrate
```

---

#### Task 3.2: Tạo Bài 13 - Ending Sounds
**Nội dung bài học:**
1. **Screen 1: Intro**
   - Lỗi phổ biến nhất của người Việt
   - "like" vs "lie", "lived" vs "live"

2. **Screen 2: Theory**
   - Ending consonants: /p/ /t/ /k/ /b/ /d/ /g/ /m/ /n/ /ŋ/ /s/ /z/
   - Ví dụ: "stop", "bed", "song"

3. **Screen 3: Practice**
   - Minimal pairs: "cap" vs "cab", "had" vs "hat"

4. **Screen 4: Challenge**
   - Sentence dictation: "I lived in a big house last week."

**File cần tạo:**
- Add to `populate_pronunciation_lessons.py`

---

#### Task 3.3: Tạo Bài 14 - Consonant Clusters
**Nội dung:**
- Initial clusters: /sp/ /st/ /sk/ /pl/ /bl/ /tr/ /dr/ /str/
  - Ví dụ: spring, street, plane, train
  
- Final clusters: /ks/ /ts/ /dz/ /mps/ /nts/
  - Ví dụ: texts, wants, lamps

**Lỗi thường gặp:**
- "spring" → "bring" (bỏ /s/)
- "street" → "stet-reet" (thêm nguyên âm vào giữa)

---

#### Task 3.4: Tạo Bài 15 - Common Vietnamese Mistakes
**Nội dung:**

1. **R vs D confusion**
   - reason → "dizzon"
   - right → "dite"
   - Practice: "The red car is right there"

2. **N vs L confusion**
   - night → "light"
   - long → "nong"

3. **The /j/ sound (yes)**
   - yes → "dét" or "zét"
   - year → "dia"

**File cần tạo:**
- Add detailed lesson content to seed command

---

### **PHASE 4: NÂNG CẤP TÍNH NĂNG TƯƠNG TÁC** ⭐ Ưu tiên thấp

#### Task 4.1: Side-by-side Audio Comparison
**Trong lesson_detail.html:**

```html
<div class="comparison-section">
    <h5>So sánh âm Anh vs Việt</h5>
    <div class="row">
        <div class="col-6">
            <button class="btn btn-primary" onclick="playEnglish()">
                <i class="fas fa-play"></i> Âm Anh chuẩn
            </button>
            <p>{{ phoneme.ipa_symbol }}</p>
        </div>
        <div class="col-6">
            <button class="btn btn-warning" onclick="playVietnamese()">
                <i class="fas fa-play"></i> Lỗi người Việt
            </button>
            <p>{{ phoneme.vietnamese_approx }}</p>
        </div>
    </div>
</div>
```

**File cần sửa:**
- `backend/templates/curriculum/pronunciation/lesson_detail.html`

---

#### Task 4.2: Vibration Check Mode (Advanced)
**Tính năng "wow":**

```javascript
// Detect microphone frequency for voiced consonants
async function checkVibration() {
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    
    // Check if low frequency (< 300Hz) has high amplitude
    const lowFreqEnergy = calculateLowFreqEnergy(analyser);
    
    if (lowFreqEnergy > THRESHOLD) {
        showMessage("✅ Cổ họng rung! Đúng rồi!");
    } else {
        showMessage("❌ Cổ họng chưa rung. Thử lại!");
    }
}
```

**File cần tạo:**
- `backend/static/js/vibration-check.js` - NEW
- Update `learning.html` to include this feature

---

#### Task 4.3: Error Heatmap Dashboard
**Hiển thị trong pronunciation progress dashboard:**

```html
<div class="error-heatmap">
    <h4>Các lỗi bạn hay mắc</h4>
    <div class="error-bars">
        <div class="error-item">
            <span>Bỏ âm cuối</span>
            <div class="bar" style="width: 75%">75%</div>
        </div>
        <div class="error-item">
            <span>Nhầm /n/ và /l/</span>
            <div class="bar" style="width: 45%">45%</div>
        </div>
    </div>
</div>
```

**Dữ liệu từ:**
- `DiscriminationAttempt` - Tính % sai cho mỗi minimal pair category
- `UserPhonemeProgress` - Phonemes có accuracy thấp

**File cần sửa:**
- `backend/templates/curriculum/pronunciation/progress.html`
- `backend/apps/curriculum/views_pronunciation.py` - Add error analysis

---

#### Task 4.4: Tongue Twister Minigame
**Sau khi hoàn thành một giai đoạn:**

```html
<div class="twister-challenge">
    <h3>🎮 Thử thách: Xoắn lưỡi!</h3>
    <p class="twister-text">
        She sells seashells by the seashore
    </p>
    <button class="btn btn-lg btn-danger" onclick="startRecording()">
        <i class="fas fa-microphone"></i> Bắt đầu (10 giây)
    </button>
</div>
```

**Scoring:**
- Basic: Check if all words detected (Speech-to-Text)
- Advanced: Measure speed (words per second)
- Leaderboard: Top 10 fastest correct readings

**File cần tạo:**
- `backend/templates/curriculum/pronunciation/twister_challenge.html` - NEW

---

### **PHASE 5: PRODUCTION SCORING (LONG-TERM)** ⭐ Tương lai

#### Task 5.1: Integrate Speech-to-Text API
**Options:**
- Google Cloud Speech-to-Text (Phoneme-level analysis)
- Azure Speech Service (Pronunciation Assessment)
- AssemblyAI (Phoneme timestamps)

**Example:**
```python
from google.cloud import speech_v1p1beta1 as speech

def analyze_pronunciation(audio_file, expected_phonemes):
    """
    Returns:
    {
        'accuracy': 85,
        'missing_phonemes': ['/t/', '/s/'],
        'incorrectly_pronounced': ['/θ/']
    }
    """
```

---

## 📅 TIMELINE ƯỚC TÍNH

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|----------------|----------|
| Phase 1 | 1.1 - 1.5 | 2-3 weeks | ⭐⭐⭐ Critical |
| Phase 2 | 2.1 - 2.3 | 1 week | ⭐⭐ High |
| Phase 3 | 3.1 - 3.4 | 2 weeks | ⭐⭐ High |
| Phase 4 | 4.1 - 4.4 | 2-3 weeks | ⭐ Medium |
| Phase 5 | 5.1 | 1-2 months | Future |

**Total:** ~6-8 weeks for Phases 1-4

---

## 🎯 KPI ĐO LƯỜNG THÀNH CÔNG

### Giai đoạn 1 (Data Foundation):
- ✅ 44+ phonemes seeded với đầy đủ metadata
- ✅ 15 pronunciation lessons published
- ✅ 100+ minimal pairs
- ✅ 4 curriculum stages created

### Giai đoạn 2 (Curriculum Flow):
- ✅ Library hiển thị theo stages
- ✅ Prerequisites hoạt động
- ✅ Dashboard hiển thị progress theo stage

### Giai đoạn 3 (Vietnamese Content):
- ✅ Tất cả phonemes có `vietnamese_comparison`
- ✅ Bài 13, 14, 15 published
- ✅ Mỗi phoneme có ít nhất 1 common mistake note

### Giai đoạn 4 (Interactive):
- ✅ Side-by-side comparison implemented
- ✅ Error heatmap showing
- ✅ Tongue twister challenges active

---

## 📝 CHECKLIST BẮT ĐẦU

- [ ] Review tài liệu phương pháp
- [ ] Backup database hiện tại
- [ ] Create feature branch: `feature/pronunciation-curriculum`
- [ ] Install dependencies (nếu cần Speech API)
- [ ] Run Phase 1 Task 1.1 (Create CurriculumStage model)

---

## 🔗 LIÊN KẾT THAM KHẢO

- [Phương pháp luyện phát âm tiếng Anh chuẩn](../Hướng dẫn/Phương pháp luyện phát âm tiếng Anh chuẩn)
- [Gap Analysis Document](untitled:Untitled-1)
- [IPA Chart](https://www.internationalphoneticassociation.org/content/ipa-chart)
- [Common Vietnamese English Mistakes](https://example.com)

---

**Người tạo:** AI Assistant  
**Ngày tạo:** 2026-01-04  
**Phiên bản:** 1.0
