# 🎴 HỆ THỐNG FLASHCARD - TÀI LIỆU TRIỂN KHAI CHI TIẾT

**Version:** 1.0  
**Date:** January 7, 2026  
**Status:** 🚧 In Progress  
**Developer:** EnglishMaster Team

---

## 📖 MỤC LỤC

1. [Tổng Quan Hệ Thống](#tổng-quan-hệ-thống)
2. [Kiến Trúc Kỹ Thuật](#kiến-trúc-kỹ-thuật)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Frontend Components](#frontend-components)
6. [Quy Trình Triển Khai](#quy-trình-triển-khai)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Guide](#deployment-guide)

---

## 1. TỔNG QUAN HỆ THỐNG

### 🎯 Mục Tiêu

Xây dựng hệ thống flashcard thông minh giúp người học tiếng Anh:
- Học từ vựng hiệu quả với thuật toán Spaced Repetition (SM-2)
- Tiến bộ từ cấp độ A1 → C1 một cách tự nhiên
- Duy trì động lực học với gamification (streak, achievements, progress)
- Phát âm chuẩn với Edge-TTS
- Trải nghiệm mượt mà, tương tác cao

### 📊 Số Liệu Hiện Tại

- **Tổng từ vựng:** 5,311 từ
- **Phân bổ:**
  - A1: 898 từ
  - A2: 866 từ
  - B1: 807 từ
  - B2: 1,426 từ
  - C1: 1,314 từ

### 🎮 Tính Năng Chính

#### Core Features
- ✅ Flashcard với flip animation 3D
- ✅ Audio phát âm tự động (Edge-TTS)
- ✅ Spaced Repetition Algorithm (SM-2)
- ✅ Progress tracking theo cấp độ
- ✅ Daily goal & streak system

#### Gamification
- 🏆 Achievement badges
- 🔥 Streak counter
- 📊 Statistics dashboard
- 🎯 Daily/weekly goals
- ⭐ Level progression

#### UX Enhancements
- 📱 Mobile-responsive (swipe gestures)
- ⌨️ Keyboard shortcuts
- 🎨 Beautiful animations
- 🌙 Dark mode support
- 🎉 Celebration effects (confetti)

---

## 2. KIẾN TRÚC KỸ THUẬT

### Tech Stack

```
Backend:
├── Django 4.2+ (REST Framework)
├── PostgreSQL / SQLite
├── Celery (async tasks)
├── Redis (caching)
└── Edge-TTS (audio generation)

Frontend:
├── Vue.js 3 (Composition API)
├── Pinia (state management)
├── Bootstrap 5 (UI framework)
├── Axios (HTTP client)
└── Canvas Confetti (animations)

Infrastructure:
├── Nginx (web server)
├── Gunicorn (WSGI)
└── AWS S3 / Local storage (media files)
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   USER BROWSER                       │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │  Vue.js 3  │  │  Pinia     │  │  Bootstrap 5 │ │
│  │ Components │←→│   Store    │  │    Styles    │ │
│  └────────────┘  └────────────┘  └──────────────┘ │
└────────────────────────┬────────────────────────────┘
                         │ HTTPS/REST API
                         ↓
┌─────────────────────────────────────────────────────┐
│                  DJANGO BACKEND                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         Django REST Framework (DRF)          │  │
│  │  ┌────────────┐  ┌──────────┐  ┌─────────┐ │  │
│  │  │   Views    │  │Serializers│  │  Auth   │ │  │
│  │  │ (ViewSets) │←→│  (DRF)   │  │  (JWT)  │ │  │
│  │  └────────────┘  └──────────┘  └─────────┘ │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │              Business Logic                   │  │
│  │  ┌────────────────┐  ┌──────────────────┐   │  │
│  │  │  SM-2 Algorithm│  │  Achievement     │   │  │
│  │  │  (Spaced Rep.) │  │  System          │   │  │
│  │  └────────────────┘  └──────────────────┘   │  │
│  │  ┌────────────────┐  ┌──────────────────┐   │  │
│  │  │  TTS Service   │  │  Progress        │   │  │
│  │  │  (Edge-TTS)    │  │  Tracker         │   │  │
│  │  └────────────────┘  └──────────────────┘   │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │              Database (ORM)                   │  │
│  │  ┌─────┐ ┌──────────┐ ┌─────────────────┐  │  │
│  │  │Word │ │Flashcard │ │UserFlashcard    │  │  │
│  │  │     │→│          │→│Progress         │  │  │
│  │  └─────┘ └──────────┘ └─────────────────┘  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                  STORAGE & CACHE                     │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │  PostgreSQL  │  │   Redis     │  │  S3/Local │ │
│  │  (Database)  │  │  (Cache)    │  │  (Media)  │ │
│  └──────────────┘  └─────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 3. DATABASE SCHEMA

### Models Overview

```python
# Core Models (Already exist - optimized)
├── Word (5,311 records)
│   └── Fields: text, pos, ipa, cefr_level, meaning_vi, audio_uk, audio_us
│
├── FlashcardDeck
│   └── Fields: name, category, level, is_public, created_by
│
├── Flashcard
│   └── Fields: word_id, deck_id, front_text, back_text, difficulty
│
└── UserFlashcardProgress (SM-2 Algorithm)
    └── Fields: user, flashcard, easiness_factor, interval, next_review_date
        
# New/Enhanced Models
├── StudySession (Enhanced)
│   └── NEW: streak_count, daily_goal, cards_goal_today
│
├── Achievement (New)
│   └── Fields: key, name, description, icon, requirement
│
└── UserAchievement (New)
    └── Fields: user, achievement, unlocked_at
```

### Detailed Schema

#### 1. Word Model (✅ Already Exists)
```python
class Word(models.Model):
    text = models.CharField(max_length=100, db_index=True)
    pos = models.CharField(max_length=50)  # Part of speech
    cefr_level = models.CharField(max_length=10, db_index=True)  # A1-C1
    ipa = models.CharField(max_length=100)  # Pronunciation
    british_ipa = models.CharField(max_length=100, blank=True)
    american_ipa = models.CharField(max_length=100, blank=True)
    meaning_vi = models.CharField(max_length=500)
    meaning_en = models.TextField(blank=True)
    example_en = models.TextField(blank=True)
    example_vi = models.TextField(blank=True)
    audio_uk = models.FileField(upload_to='audio/words/uk/', blank=True)
    audio_us = models.FileField(upload_to='audio/words/us/', blank=True)
    
    class Meta:
        unique_together = [['text', 'pos', 'cefr_level']]
```

#### 2. Flashcard Model (✅ Already Exists)
```python
class Flashcard(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    deck = models.ForeignKey(FlashcardDeck, on_delete=models.CASCADE)
    front_text = models.CharField(max_length=500)
    back_text = models.TextField()
    difficulty = models.IntegerField(default=3)  # 1-5
    
    class Meta:
        unique_together = [['word', 'deck']]
```

#### 3. UserFlashcardProgress (✅ Already Exists - SM-2 Algorithm)
```python
class UserFlashcardProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    
    # SM-2 Algorithm fields
    easiness_factor = models.FloatField(default=2.5)  # 1.3-2.5
    interval = models.IntegerField(default=1)  # Days until next review
    repetitions = models.IntegerField(default=0)
    next_review_date = models.DateTimeField()
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    last_quality = models.IntegerField(null=True, blank=True)  # 0-5
    
    # Statistics
    total_reviews = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    is_mastered = models.BooleanField(default=False)
    
    def calculate_next_review(self, quality):
        """SM-2 Algorithm implementation"""
        # Update E-Factor
        ef = self.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        self.easiness_factor = max(1.3, ef)
        
        # Update interval
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.easiness_factor)
        
        # Schedule next review
        self.next_review_date = timezone.now() + timedelta(days=self.interval)
        self.last_reviewed_at = timezone.now()
        self.last_quality = quality
        self.total_reviews += 1
        
        if quality >= 3:
            self.total_correct += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
        else:
            self.streak = 0
        
        self.save()
```

#### 4. StudySession (🔧 Enhance Existing)
```python
class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deck = models.ForeignKey(FlashcardDeck, on_delete=models.CASCADE)
    
    # Session data
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    cards_studied = models.IntegerField(default=0)
    cards_correct = models.IntegerField(default=0)
    time_spent_seconds = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0)
    
    # NEW: Streak & Goals
    streak_count = models.IntegerField(default=0)
    daily_goal = models.IntegerField(default=20)
    cards_goal_today = models.IntegerField(default=0)
    is_goal_reached = models.BooleanField(default=False)
```

#### 5. Achievement (🆕 New Model)
```python
class Achievement(models.Model):
    CATEGORY_CHOICES = [
        ('milestone', 'Milestone'),
        ('streak', 'Streak'),
        ('speed', 'Speed'),
        ('mastery', 'Mastery'),
    ]
    
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Emoji or icon class
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Requirements (JSON field)
    requirement_type = models.CharField(max_length=50)  # 'cards_learned', 'streak_days', etc.
    requirement_value = models.IntegerField()
    
    # Rewards
    points = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'requirement_value']

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'achievement']]
```

---

## 4. API ENDPOINTS

### Authentication
All endpoints require JWT authentication except where noted.

### Base URL
```
Development: http://127.0.0.1:8000/api/v1
Production: https://api.englishmaster.com/api/v1
```

### Endpoint List

#### 📚 Flashcard Study Endpoints

##### 1. Start Study Session
```http
POST /api/v1/flashcards/study/session/start/

Request Body:
{
    "deck_id": 1,           // Optional: specific deck
    "level": "A1",          // Optional: filter by level
    "card_count": 20        // Optional: number of cards (default: 20)
}

Response 200:
{
    "session_id": 123,
    "cards": [
        {
            "id": 1,
            "word": {
                "id": 1,
                "text": "abandon",
                "pos": "verb",
                "ipa": "/əˈbændən/",
                "meaning_vi": "bỏ rơi",
                "example_en": "She abandoned her car",
                "cefr_level": "B2"
            },
            "difficulty": 3,
            "last_reviewed": null,
            "times_reviewed": 0
        }
        // ... more cards
    ],
    "daily_progress": {
        "learned_today": 5,
        "goal": 20,
        "percentage": 25
    },
    "streak": {
        "current": 7,
        "longest": 12
    }
}
```

##### 2. Review Card
```http
POST /api/v1/flashcards/study/card/{card_id}/review/

Request Body:
{
    "quality": 4,           // 0-5 (SM-2 quality rating)
    "time_spent": 8         // seconds spent on card
}

Response 200:
{
    "next_review_date": "2026-01-08T10:30:00Z",
    "interval": 1,          // days until next review
    "easiness_factor": 2.6,
    "is_mastered": false,
    "achievements_unlocked": [
        {
            "key": "first_10_cards",
            "name": "🎓 First Steps",
            "description": "Learned your first 10 cards"
        }
    ],
    "next_card": {
        // Next card data or null if session complete
    }
}
```

##### 3. Get Due Cards
```http
GET /api/v1/flashcards/study/due/

Query Parameters:
?level=A1&limit=20

Response 200:
{
    "cards": [...],
    "total_due": 45,
    "by_level": {
        "A1": 10,
        "A2": 15,
        "B1": 20
    }
}
```

##### 4. End Session
```http
POST /api/v1/flashcards/study/session/{session_id}/end/

Request Body:
{
    "cards_studied": 20,
    "cards_correct": 17,
    "time_spent": 900       // seconds
}

Response 200:
{
    "session_stats": {
        "cards_studied": 20,
        "accuracy": 85,
        "time_spent": "15 minutes",
        "avg_time_per_card": 45
    },
    "achievements_unlocked": [],
    "streak_updated": true,
    "new_streak": 8,
    "goal_reached": true
}
```

#### 🔊 Audio Endpoints

##### 5. Get Word Audio
```http
GET /api/v1/audio/word/{word_id}/

Query Parameters:
?voice=us_female&speed=normal

Voices: us_female, us_male, uk_female, uk_male
Speed: slow, normal, fast

Response: audio/mp3 stream
```

##### 6. Generate Audio (Async)
```http
POST /api/v1/audio/generate/

Request Body:
{
    "word_id": 1,
    "voice": "us_female",
    "speed": "normal"
}

Response 202:
{
    "task_id": "abc123",
    "status": "processing",
    "message": "Audio generation started"
}
```

#### 📊 Progress & Stats Endpoints

##### 7. Dashboard Statistics
```http
GET /api/v1/progress/dashboard/

Response 200:
{
    "today": {
        "cards_learned": 15,
        "time_spent": 25,       // minutes
        "accuracy": 85,
        "goal_progress": 75     // percentage
    },
    "week": {
        "cards_learned": 98,
        "time_spent": 180,
        "accuracy": 82,
        "days_active": 6
    },
    "streak": {
        "current": 8,
        "longest": 15,
        "freeze_available": true
    },
    "levels": {
        "A1": { "learned": 120, "total": 898, "mastered": 45 },
        "A2": { "learned": 50, "total": 866, "mastered": 10 },
        "B1": { "learned": 0, "total": 807, "mastered": 0 }
    },
    "upcoming_reviews": 23,
    "total_time": 1250          // minutes all time
}
```

##### 8. Achievement List
```http
GET /api/v1/achievements/

Response 200:
{
    "unlocked": [
        {
            "id": 1,
            "key": "first_10_cards",
            "name": "🎓 First Steps",
            "description": "Learned your first 10 cards",
            "unlocked_at": "2026-01-05T10:00:00Z",
            "category": "milestone"
        }
    ],
    "locked": [
        {
            "id": 2,
            "key": "streak_7_days",
            "name": "🔥 Week Warrior",
            "description": "Maintain a 7-day streak",
            "progress": 5,              // current progress
            "requirement": 7,           // required value
            "percentage": 71
        }
    ]
}
```

#### 🎯 Deck Management Endpoints

##### 9. List Decks
```http
GET /api/v1/decks/

Response 200:
{
    "decks": [
        {
            "id": 1,
            "name": "Oxford 3000 - A1",
            "level": "A1",
            "icon": "📚",
            "card_count": 898,
            "mastered_count": 45,
            "new_count": 778,
            "review_count": 75,
            "is_official": true,
            "progress_percentage": 13
        }
    ]
}
```

##### 10. Create Custom Deck
```http
POST /api/v1/decks/

Request Body:
{
    "name": "My Vocabulary",
    "description": "Personal collection",
    "icon": "📖",
    "is_public": false
}

Response 201:
{
    "id": 10,
    "name": "My Vocabulary",
    "card_count": 0
}
```

---

## 5. FRONTEND COMPONENTS

### Component Tree

```
App.vue
└── views/
    ├── FlashcardDashboard.vue (Main dashboard)
    │   ├── DailyGoalCard.vue
    │   ├── StreakCounter.vue
    │   ├── LevelProgressCircles.vue
    │   ├── DeckGrid.vue
    │   │   └── DeckCard.vue
    │   └── UpcomingReviews.vue
    │
    ├── FlashcardStudy.vue (Study session)
    │   ├── StudyHeader.vue
    │   │   ├── SessionProgress.vue
    │   │   └── DailyProgress.vue
    │   ├── FlashcardCard.vue (Main card)
    │   │   ├── CardFront.vue
    │   │   └── CardBack.vue
    │   ├── AudioPlayer.vue
    │   ├── QualityRatingButtons.vue
    │   ├── SwipeHints.vue
    │   └── KeyboardShortcutsHint.vue
    │
    ├── SessionComplete.vue (End of session)
    │   ├── SessionStats.vue
    │   ├── AchievementUnlocked.vue
    │   └── ContinueOptions.vue
    │
    └── ProgressDashboard.vue
        ├── StatisticsCards.vue
        ├── ProgressChart.vue
        ├── AchievementGrid.vue
        └── ReviewCalendar.vue
```

### State Management (Pinia)

```javascript
// stores/flashcard.js
export const useFlashcardStore = defineStore('flashcard', {
  state: () => ({
    // Session state
    currentSession: null,
    cards: [],
    currentIndex: 0,
    isFlipped: false,
    
    // Progress
    dailyProgress: {
      learned: 0,
      goal: 20,
      percentage: 0
    },
    
    // Streak
    streak: {
      current: 0,
      longest: 0
    },
    
    // UI state
    isLoading: false,
    showConfetti: false,
    achievements: []
  }),
  
  getters: {
    currentCard: (state) => state.cards[state.currentIndex],
    hasNextCard: (state) => state.currentIndex < state.cards.length - 1,
    sessionProgress: (state) => ({
      current: state.currentIndex + 1,
      total: state.cards.length,
      percentage: ((state.currentIndex + 1) / state.cards.length) * 100
    })
  },
  
  actions: {
    async startSession(level, cardCount = 20) { /* ... */ },
    async reviewCard(quality) { /* ... */ },
    flipCard() { /* ... */ },
    nextCard() { /* ... */ },
    async playAudio(wordId, voice = 'us_female') { /* ... */ }
  }
})
```

---

## 6. QUY TRÌNH TRIỂN KHAI

### Phase 1: Backend Foundation (2-3 days) - IN PROGRESS ✅

#### Day 1: Database & Models
- ✅ Review existing models
- ⏳ Create Achievement model
- ⏳ Enhance StudySession model
- ⏳ Create migrations
- ⏳ Create utility: generate flashcards from words

#### Day 2: API Implementation
- ⏳ Implement study session endpoints
- ⏳ Implement review card endpoint
- ⏳ Implement progress endpoints
- ⏳ Implement achievement system
- ⏳ Write unit tests

#### Day 3: Audio Service
- ⏳ Setup Edge-TTS service
- ⏳ Implement audio generation
- ⏳ Setup audio caching (Redis)
- ⏳ Create audio streaming endpoint

### Phase 2: Frontend Components (3-4 days)

#### Day 4: Setup & Store
- Setup Vue 3 project structure
- Install dependencies (Pinia, Axios, Bootstrap)
- Create Pinia store
- Setup API client

#### Day 5: Dashboard UI
- Create dashboard layout
- Implement deck list
- Create progress widgets
- Add streak counter

#### Day 6-7: Study Session UI
- Create flashcard card component
- Implement flip animation
- Add audio player
- Create rating buttons
- Add swipe gestures
- Implement keyboard shortcuts

### Phase 3: Integration & Polish (2 days)

#### Day 8: Integration
- Connect frontend to backend
- Test all flows
- Fix bugs
- Add error handling

#### Day 9: Polish & Testing
- Add loading states
- Implement confetti animation
- Mobile responsive testing
- Cross-browser testing
- Performance optimization

### Phase 4: Deployment (1 day)

#### Day 10: Deploy
- Production settings
- Deploy backend
- Deploy frontend
- Setup CDN for audio
- Monitor and fix issues

---

## 7. TESTING STRATEGY

### Unit Tests (Backend)
```python
# tests/test_flashcard_study.py
class FlashcardStudyTest(TestCase):
    def test_start_session(self)
    def test_review_card_sm2_algorithm(self)
    def test_achievement_unlock(self)
    def test_streak_calculation(self)
    def test_audio_generation(self)
```

### Integration Tests
```python
# tests/test_flashcard_integration.py
class FlashcardIntegrationTest(TestCase):
    def test_complete_study_session(self)
    def test_multi_day_streak(self)
    def test_level_progression(self)
```

### E2E Tests (Frontend)
```javascript
// tests/e2e/flashcard.spec.js
describe('Flashcard Study Flow', () => {
  it('should complete a study session')
  it('should unlock achievement')
  it('should update streak')
  it('should play audio')
})
```

---

## 8. DEPLOYMENT GUIDE

### Environment Variables
```bash
# Backend (.env)
DJANGO_SECRET_KEY=xxx
DATABASE_URL=xxx
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=xxx          # For S3 audio storage
AWS_SECRET_ACCESS_KEY=xxx
CELERY_BROKER_URL=xxx
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    environment:
      - VUE_APP_API_URL=https://api.englishmaster.com
  
  db:
    image: postgres:14
  
  redis:
    image: redis:7-alpine
```

### Production Checklist
- [ ] Enable HTTPS
- [ ] Setup CDN for static files
- [ ] Enable Gzip compression
- [ ] Setup monitoring (Sentry)
- [ ] Configure backup strategy
- [ ] Setup CI/CD pipeline
- [ ] Load testing (100+ concurrent users)

---

## 📈 METRICS & KPIs

### Success Metrics
| Metric | Target | Current |
|--------|--------|---------|
| Daily Active Users | 70% | TBD |
| Avg Cards/Session | 15-20 | TBD |
| Session Completion | >80% | TBD |
| Avg Session Time | 10-15 min | TBD |
| 7-Day Streak Rate | >50% | TBD |
| User Satisfaction | 4.5+ ⭐ | TBD |

### Technical Metrics
- API Response Time: <200ms (p95)
- Page Load Time: <2s
- Audio Load Time: <500ms
- Uptime: 99.9%

---

## 🔧 TROUBLESHOOTING

### Common Issues

1. **Audio not playing**
   - Check Edge-TTS service status
   - Verify audio file exists
   - Check browser audio permissions

2. **Cards not loading**
   - Verify user authentication
   - Check database connection
   - Review API logs

3. **Streak not updating**
   - Check timezone settings
   - Verify session completion
   - Review streak calculation logic

---

## 📞 SUPPORT & MAINTENANCE

### Daily Tasks
- Monitor error logs
- Check audio generation queue
- Review user feedback

### Weekly Tasks
- Database backup
- Performance review
- Feature usage analytics

### Monthly Tasks
- Security audit
- Dependency updates
- User satisfaction survey

---

**Document Version:** 1.0  
**Last Updated:** January 7, 2026  
**Next Review:** January 14, 2026
