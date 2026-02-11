# 📚 KẾ HOẠCH TRIỂN KHAI HỆ THỐNG TỪ VỰNG + FLASHCARD

## 🎯 MỤC TIÊU TỔNG QUAN

Xây dựng hệ thống học từ vựng toàn diện với:
- **Oxford 3000** (A1-B2): 3000 từ cơ bản
- **Oxford 5000** (B2-C1): thêm 2000 từ nâng cao
- **Flashcard System** với thuật toán SM-2 (Spaced Repetition)
- **Tích hợp với Pronunciation Lessons** đã có

---

## 📊 PHÂN TÍCH HIỆN TRẠNG

### ✅ Đã có
1. **UI Flashcard** (`public/flashcard.html`):
   - 3D flip animation
   - Vue.js 3
   - Timer & progress tracking
   - Web Speech API for pronunciation
   - Statistics tracking (easy/hard/again)

2. **Pronunciation System**:
   - 27 lessons (monophthongs, diphthongs, consonants)
   - Phoneme models với IPA
   - Audio TTS integration

3. **User Management**:
   - JWT authentication
   - User progress tracking

### ❌ Thiếu
1. **Word Database**: Chưa có model lưu từ vựng
2. **Data Import**: Chưa có scripts import Oxford CSV
3. **Flashcard Backend**: Chưa có API cho flashcard system
4. **SM-2 Algorithm**: Chưa implement spaced repetition
5. **Vietnamese Translations**: Chưa có nghĩa tiếng Việt tự động
6. **Integration**: Flashcard chưa kết nối với pronunciation

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                        VOCABULARY SYSTEM                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│     Word     │────────>│   Flashcard  │<────────│UserFlashcard │
│              │  1:N    │              │   N:N   │   Progress   │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │         │ id (PK)      │         │ id (PK)      │
│ text         │         │ word_id (FK) │         │ user_id (FK) │
│ pos          │         │ deck_id (FK) │         │ flashcard_id │
│ cefr_level   │         │ front_text   │         │ easiness     │
│ ipa          │         │ back_text    │         │ interval     │
│ meaning_vi   │         │ hint         │         │ repetitions  │
│ meaning_en   │         │ difficulty   │         │ next_review  │
│ example_en   │         │ tags         │         │ last_review  │
│ example_vi   │         │ audio_url    │         │ quality      │
│ collocations │         │ image_url    │         │ studied_at   │
│ mnemonic     │         │ created_at   │         └──────────────┘
│ frequency    │         └──────────────┘               │
│ british_ipa  │                │                       │
│ american_ipa │                │                       │
│ audio_uk     │                │                       │
│ audio_us     │                │                       │
│ etymology    │                V                       │
│ synonyms     │         ┌──────────────┐              │
│ antonyms     │         │ FlashcardDeck│              │
│ register     │         ├──────────────┤              │
│ created_at   │         │ id (PK)      │              │
│ updated_at   │         │ name         │              │
└──────────────┘         │ description  │              │
       │                 │ level        │              │
       │                 │ category     │              │
       │                 │ is_public    │              │
       │                 │ created_by   │              │
       │                 └──────────────┘              │
       │                                                │
       │                                                │
       V                                                V
┌──────────────┐                              ┌──────────────┐
│WordPhoneme   │                              │ StudySession │
│  (M2M)       │                              ├──────────────┤
├──────────────┤                              │ id (PK)      │
│ word_id (FK) │                              │ user_id (FK) │
│ phoneme_id   │                              │ deck_id (FK) │
└──────────────┘                              │ started_at   │
                                              │ ended_at     │
                                              │ cards_studied│
                                              │ accuracy     │
                                              │ time_spent   │
                                              └──────────────┘
```

---

## 📋 KẾ HOẠCH TRIỂN KHAI 6 PHASES

### **PHASE 1: Database Foundation (2-3 ngày)**

#### Step 1.1: Create Word Model ✅
**File**: `backend/apps/vocabulary/models.py`

```python
class Word(models.Model):
    """Oxford word with full metadata"""
    # Basic info
    text = models.CharField(max_length=100, unique=True, db_index=True)
    pos = models.CharField(max_length=50)  # Part of speech
    cefr_level = models.CharField(max_length=10, db_index=True)  # A1, A2, B1, B2, C1, C2
    
    # Pronunciation
    ipa = models.CharField(max_length=100, blank=True)
    british_ipa = models.CharField(max_length=100, blank=True)
    american_ipa = models.CharField(max_length=100, blank=True)
    
    # Meanings
    meaning_vi = models.CharField(max_length=500)
    meaning_en = models.TextField(blank=True)
    
    # Examples
    example_en = models.TextField(blank=True)
    example_vi = models.TextField(blank=True)
    
    # Learning aids
    collocations = models.CharField(max_length=500, blank=True)
    mnemonic = models.TextField(blank=True)
    etymology = models.TextField(blank=True)
    
    # Related words
    synonyms = models.CharField(max_length=500, blank=True)
    antonyms = models.CharField(max_length=500, blank=True)
    
    # Frequency & register
    frequency_rank = models.IntegerField(null=True, blank=True)
    register = models.CharField(max_length=50, blank=True)  # formal, informal, slang
    
    # Audio
    audio_uk = models.FileField(upload_to='audio/words/uk/', blank=True)
    audio_us = models.FileField(upload_to='audio/words/us/', blank=True)
    
    # Image
    image = models.ImageField(upload_to='images/words/', blank=True)
    
    # Relationships
    phonemes = models.ManyToManyField('curriculum.Phoneme', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['frequency_rank', 'text']
        indexes = [
            models.Index(fields=['cefr_level', 'text']),
            models.Index(fields=['frequency_rank']),
        ]
    
    def __str__(self):
        return f"{self.text} ({self.cefr_level})"
```

#### Step 1.2: Create Flashcard Models ✅
**File**: `backend/apps/vocabulary/models.py`

```python
class FlashcardDeck(models.Model):
    """Collection of flashcards"""
    CATEGORIES = [
        ('oxford', 'Oxford Words'),
        ('pronunciation', 'Pronunciation'),
        ('grammar', 'Grammar'),
        ('idioms', 'Idioms'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    level = models.CharField(max_length=10, blank=True)  # A1, B1, etc
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    icon = models.CharField(max_length=100, default='📚')
    color = models.CharField(max_length=7, default='#F47C26')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.level})"
    
    @property
    def card_count(self):
        return self.flashcards.count()


class Flashcard(models.Model):
    """Individual flashcard"""
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='flashcards')
    deck = models.ForeignKey(FlashcardDeck, on_delete=models.CASCADE, related_name='flashcards')
    
    # Front side (question)
    front_text = models.CharField(max_length=500)  # Usually the English word
    front_type = models.CharField(max_length=50, default='word')  # word, sentence, image
    
    # Back side (answer)
    back_text = models.TextField()  # Meaning, translation, explanation
    back_example = models.TextField(blank=True)
    
    # Additional info
    hint = models.CharField(max_length=500, blank=True)
    difficulty = models.IntegerField(default=3)  # 1-5
    tags = models.CharField(max_length=500, blank=True)
    
    # Media
    audio_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    
    # Order in deck
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['word', 'deck']
    
    def __str__(self):
        return f"{self.front_text} -> {self.back_text[:50]}"


class UserFlashcardProgress(models.Model):
    """SM-2 algorithm implementation for spaced repetition"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    
    # SM-2 Algorithm fields
    easiness_factor = models.FloatField(default=2.5)  # E-Factor (1.3 - 2.5)
    interval = models.IntegerField(default=1)  # Days until next review
    repetitions = models.IntegerField(default=0)  # Number of correct repetitions
    
    # Review scheduling
    next_review_date = models.DateTimeField()
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Quality of last recall (0-5)
    # 0: Complete blackout
    # 1: Incorrect, but upon seeing answer it felt familiar
    # 2: Incorrect, but upon seeing answer it seemed easy
    # 3: Correct, but required significant effort
    # 4: Correct, after some hesitation
    # 5: Perfect recall
    last_quality = models.IntegerField(null=True, blank=True)
    
    # Statistics
    total_reviews = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_incorrect = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)  # Current correct streak
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'flashcard']
        indexes = [
            models.Index(fields=['user', 'next_review_date']),
        ]
    
    def calculate_next_review(self, quality):
        """
        SM-2 Algorithm implementation
        quality: 0-5 (user's rating of recall)
        """
        from datetime import timedelta
        from django.utils import timezone
        
        # Update E-Factor
        ef = self.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ef = max(1.3, ef)  # Minimum E-Factor is 1.3
        self.easiness_factor = ef
        
        # Update repetitions
        if quality < 3:
            # Incorrect response: reset repetitions
            self.repetitions = 0
            self.interval = 1
        else:
            # Correct response
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = int(self.interval * ef)
        
        # Set next review date
        self.next_review_date = timezone.now() + timedelta(days=self.interval)
        self.last_reviewed_at = timezone.now()
        self.last_quality = quality
        
        # Update statistics
        self.total_reviews += 1
        if quality >= 3:
            self.total_correct += 1
            self.streak += 1
        else:
            self.total_incorrect += 1
            self.streak = 0
        
        self.save()


class StudySession(models.Model):
    """Track study sessions"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    deck = models.ForeignKey(FlashcardDeck, on_delete=models.CASCADE)
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    cards_studied = models.IntegerField(default=0)
    cards_correct = models.IntegerField(default=0)
    cards_incorrect = models.IntegerField(default=0)
    
    accuracy = models.FloatField(default=0)  # Percentage
    time_spent_seconds = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.deck.name} ({self.started_at.date()})"
```

#### Step 1.3: Create migrations
```bash
python backend/manage.py makemigrations vocabulary
python backend/manage.py migrate
```

---

### **PHASE 2: Data Import (2-3 ngày)**

#### Step 2.1: Install Dependencies
```bash
pip install eng-to-ipa
pip install deep-translator
pip install PyDictionary
```

#### Step 2.2: Create Import Command
**File**: `backend/apps/vocabulary/management/commands/import_oxford_words.py`

Xem implementation chi tiết trong file này (sẽ tạo ở bước sau).

#### Step 2.3: Run Import
```bash
# Import Oxford 3000
python backend/manage.py import_oxford_words The_Oxford_3000.csv --level A1-B2

# Import Oxford 5000
python backend/manage.py import_oxford_words The_Oxford_5000.csv --level B2-C1
```

---

### **PHASE 3: API Development (3-4 ngày)**

#### Step 3.1: Serializers
**File**: `backend/apps/vocabulary/serializers.py`

```python
class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'


class FlashcardSerializer(serializers.ModelSerializer):
    word = WordSerializer(read_only=True)
    
    class Meta:
        model = Flashcard
        fields = '__all__'


class UserFlashcardProgressSerializer(serializers.ModelSerializer):
    flashcard = FlashcardSerializer(read_only=True)
    
    class Meta:
        model = UserFlashcardProgress
        fields = '__all__'
```

#### Step 3.2: API Endpoints
**File**: `backend/apps/vocabulary/api_views.py`

```python
# Endpoint list:
GET    /api/v1/vocabulary/words/                    # List words
GET    /api/v1/vocabulary/words/{id}/               # Word detail
GET    /api/v1/vocabulary/words/search/             # Search words
GET    /api/v1/vocabulary/words/random/             # Random word

GET    /api/v1/vocabulary/decks/                    # List decks
GET    /api/v1/vocabulary/decks/{id}/               # Deck detail
POST   /api/v1/vocabulary/decks/                    # Create deck
PUT    /api/v1/vocabulary/decks/{id}/               # Update deck
DELETE /api/v1/vocabulary/decks/{id}/               # Delete deck

GET    /api/v1/vocabulary/flashcards/               # List flashcards
GET    /api/v1/vocabulary/flashcards/due/           # Cards due for review
POST   /api/v1/vocabulary/flashcards/{id}/review/   # Submit review
GET    /api/v1/vocabulary/flashcards/stats/         # User statistics

POST   /api/v1/vocabulary/study/start/              # Start study session
POST   /api/v1/vocabulary/study/end/                # End study session
GET    /api/v1/vocabulary/study/history/            # Study history
```

---

### **PHASE 4: Frontend Integration (4-5 ngày)**

#### Step 4.1: Update Flashcard Page
Convert `public/flashcard.html` thành Django template với Vue.js:

**File**: `backend/templates/vocabulary/flashcard_study.html`

Thay đổi chính:
- Load data từ API thay vì hardcoded
- Implement SM-2 algorithm submission
- Add deck selection
- Add progress tracking
- Add offline support với IndexedDB

#### Step 4.2: Create Deck Library Page
**File**: `backend/templates/vocabulary/deck_library.html`

Features:
- Grid view của các decks
- Filter by level (A1, A2, B1, B2, C1)
- Filter by category
- Show card count and progress
- Search functionality

#### Step 4.3: Create Word Detail Page
**File**: `backend/templates/vocabulary/word_detail.html`

Features:
- Full word information
- Audio playback (UK & US)
- Example sentences
- Phoneme breakdown (link to pronunciation lessons)
- Related words (synonyms, antonyms)
- Add to custom deck

---

### **PHASE 5: Integration with Pronunciation (2-3 ngày)**

#### Step 5.1: Link Words to Phonemes
Tự động link words với phonemes based on IPA:

```python
def link_word_to_phonemes(word):
    """Extract phonemes from IPA and link to Word"""
    ipa = word.ipa.strip('/')
    phonemes = Phoneme.objects.filter(ipa_symbol__in=extract_phonemes(ipa))
    word.phonemes.set(phonemes)
```

#### Step 5.2: Create Pronunciation Flashcards
Tự động tạo flashcards cho pronunciation lessons:

```python
def create_pronunciation_flashcards():
    """Create flashcards from minimal pairs"""
    for pair in MinimalPair.objects.all():
        Flashcard.objects.create(
            front_text=f"{pair.word_1} vs {pair.word_2}",
            back_text=pair.difference_note_vi,
            # ...
        )
```

---

### **PHASE 6: Advanced Features (5-7 ngày)**

#### Step 6.1: Personalized Learning Path
- Recommend words based on user level
- Identify weak words (low accuracy)
- Suggest related words to learn together

#### Step 6.2: Gamification
- Daily streak tracking
- XP system (integrate with pronunciation XP)
- Leaderboard
- Achievements/badges

#### Step 6.3: Analytics Dashboard
- Words learned per day/week/month
- Retention curve
- Time spent studying
- Accuracy trends

#### Step 6.4: Mobile PWA Optimization
- Offline mode với service worker
- Background sync for progress
- Push notifications for due cards

---

## 🚀 IMPLEMENTATION PRIORITY

### High Priority (Must Have)
1. ✅ Word model với Vietnamese meanings
2. ✅ Import Oxford 3000 data
3. ✅ Flashcard system với SM-2
4. ✅ Basic API endpoints
5. ✅ Frontend integration

### Medium Priority (Should Have)
6. ✅ Pronunciation integration
7. ✅ Deck management
8. ✅ Study statistics
9. ✅ Search functionality

### Low Priority (Nice to Have)
10. ⏳ Custom user decks
11. ⏳ Gamification
12. ⏳ Advanced analytics
13. ⏳ Social features

---

## 📅 TIMELINE

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | 2-3 days | Database models + migrations |
| Phase 2 | 2-3 days | Import Oxford CSV data |
| Phase 3 | 3-4 days | API development + testing |
| Phase 4 | 4-5 days | Frontend integration |
| Phase 5 | 2-3 days | Pronunciation integration |
| Phase 6 | 5-7 days | Advanced features |
| **Total** | **18-25 days** | **Complete system** |

---

## 🎨 UI/UX DESIGN PRINCIPLES

### Flashcard Design
1. **Minimalist**: Focus on word only (no distractions)
2. **Visual Hierarchy**: Word > IPA > Example > Note
3. **Color Coding**: 
   - A1: Green (Beginner)
   - A2: Blue (Elementary)
   - B1: Orange (Intermediate)
   - B2: Purple (Upper-Intermediate)
   - C1: Red (Advanced)

### Learning Flow
```
Deck Selection → Study Mode → Card Review → Results → Recommendations
```

### Feedback System
- **Instant**: Show correctness immediately
- **Encouraging**: Celebrate streaks
- **Informative**: Show why answer is correct/incorrect
- **Progressive**: Show improvement over time

---

## 📊 SUCCESS METRICS

### Engagement
- Daily Active Users (DAU)
- Average session duration (target: 10-15 minutes)
- Cards studied per session (target: 20-30)

### Learning Effectiveness
- Retention rate (target: 80% after 7 days)
- Accuracy improvement over time
- Time to mastery per word (target: 5-7 reviews)

### System Performance
- API response time < 200ms
- Offline mode success rate > 95%
- Data sync success rate > 99%

---

## 🔧 TECHNICAL STACK

### Backend
- Django 5.2.9
- PostgreSQL
- Django REST Framework
- Celery (for background tasks)

### Frontend
- Vue.js 3
- Bootstrap 5
- IndexedDB (offline storage)
- Service Worker (PWA)

### Data Processing
- eng-to-ipa (IPA generation)
- deep-translator (Vietnamese translation)
- PyDictionary (English definitions)

---

## 📝 NEXT STEPS

### Immediate Actions (Today)
1. ✅ Create `vocabulary` app in Django
2. ✅ Design complete database schema
3. ✅ Create models.py
4. ✅ Run migrations

### Tomorrow
1. ✅ Create import command
2. ✅ Parse Oxford CSV files
3. ✅ Test data import

### Next Week
1. ✅ Build API endpoints
2. ✅ Create serializers
3. ✅ Write tests
4. ✅ Frontend integration

---

## 🎯 ULTIMATE GOAL

> "Mỗi người Việt học tiếng Anh đều có thể nhớ và sử dụng 3000-5000 từ vựng quan trọng nhất một cách tự nhiên và lâu dài thông qua hệ thống flashcard khoa học."

---

**Created**: December 19, 2025  
**Author**: AI Assistant  
**Version**: 1.0  
**Status**: Ready for Implementation 🚀
