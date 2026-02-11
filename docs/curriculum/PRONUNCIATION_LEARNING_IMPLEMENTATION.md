# 🎯 KẾ HOẠCH TRIỂN KHAI HỆ THỐNG HỌC PHÁT ÂM IPA

**Mục tiêu:** Kết nối các phần rời rạc thành quy trình học 4 bước SMART  
**Timeline:** 2 tuần (10 ngày làm việc)  
**Status:** READY TO IMPLEMENT

---

## 📊 PHÂN TÍCH GAP & GIẢI PHÁP

### ✅ Đã Có (Foundation)
- ✅ User authentication & profile system
- ✅ Database models: Phoneme, MinimalPair, AudioSource
- ✅ TTS infrastructure với Edge-TTS
- ✅ Template architecture với Bootstrap 5 + Vue 3
- ✅ Design system (colors, typography, spacing)

### ❌ Thiếu (Implementation Gap)
- ❌ **Learning Flow Logic** - 4 bước SMART
- ❌ **Stage Tracking** - Progress với unlock mechanism
- ❌ **Discrimination Practice** - Core component
- ❌ **Production Practice** - Audio recording & comparison
- ❌ **Guided Navigation** - User journey map

---

## 🗓️ IMPLEMENTATION PLAN - 10 DAYS

### **SPRINT 1: DATABASE & API FOUNDATION (Day 1-3)**

#### Day 1: Database Schema Extension
**Goal:** Thêm stage tracking vào UserPhonemeProgress

**Tasks:**
1. ✅ Extend UserPhonemeProgress model với stage fields
2. ✅ Create migration 0010_userphonemeprogress_stages
3. ✅ Add helper methods: can_practice_discrimination(), can_practice_production()
4. ✅ Write model tests

**Files to modify:**
- `backend/apps/curriculum/models/pronunciation.py`
- `backend/tests/test_pronunciation/test_models.py`

**Deliverable:** Migration file + 10 unit tests

---

#### Day 2: API Endpoints for Learning Flow
**Goal:** Create REST API endpoints cho từng stage

**Tasks:**
1. ✅ POST `/api/v1/pronunciation/phoneme/<id>/discover/` - Mark as discovered
2. ✅ POST `/api/v1/pronunciation/phoneme/<id>/start-learning/` - Start theory
3. ✅ GET `/api/v1/pronunciation/phoneme/<id>/discrimination/quiz/` - Get quiz
4. ✅ POST `/api/v1/pronunciation/phoneme/<id>/discrimination/submit/` - Submit answer
5. ✅ GET `/api/v1/pronunciation/phoneme/<id>/production/reference/` - Get reference audio
6. ✅ POST `/api/v1/pronunciation/phoneme/<id>/production/submit/` - Submit recording
7. ✅ GET `/api/v1/pronunciation/progress/` - User overall progress

**Files to create:**
- `backend/apps/curriculum/api/pronunciation_views.py`
- `backend/apps/curriculum/serializers/pronunciation_serializers.py`
- `backend/apps/curriculum/urls.py` (extend)

**Deliverable:** 7 API endpoints + Postman collection

---

#### Day 3: API Testing
**Goal:** Comprehensive API tests

**Tasks:**
1. ✅ Test discovery endpoint (201 created, 400 validation)
2. ✅ Test discrimination quiz (random selection, minimal pairs)
3. ✅ Test discrimination submit (correct/incorrect handling)
4. ✅ Test unlock logic (can't skip to production without 80% accuracy)
5. ✅ Test progress aggregation

**Files to create:**
- `backend/tests/test_pronunciation/test_api_endpoints.py`

**Deliverable:** 25+ API tests với 100% coverage

---

### **SPRINT 2: FRONTEND - DISCOVERY & LEARNING (Day 4-5)**

#### Day 4: Phoneme Discovery Page
**Goal:** Interactive IPA chart với progress tracking

**Tasks:**
1. ✅ Create template: `templates/public/pronunciation/discover.html`
2. ✅ Vue component: PhonemesDiscoveryGrid
3. ✅ Features:
   - Display 44 phonemes in categorized grid
   - Show discovery progress (badge: "Discovered 12/44")
   - Click phoneme → Play audio + Mark as discovered
   - Visual indicator: discovered (✓), learning (📖), mastered (⭐)
4. ✅ CSS according to TEMPLATE_ARCHITECTURE
5. ✅ Responsive design (mobile-first)

**Files to create:**
- `backend/templates/public/pronunciation/discover.html`
- `backend/static/js/pronunciation/discovery.js`
- `backend/static/css/pronunciation.css`

**Design Compliance:**
- Colors: `--primary-orange`, `--primary-dark`
- Typography: `--font-heading: Montserrat`, `--font-body: Open Sans`
- Spacing: CSS variables from design system
- Shadows: `--shadow-md` on hover

**Deliverable:** Working discovery page + responsive

---

#### Day 5: Phoneme Learning Detail Page
**Goal:** Theory page với mouth diagrams

**Tasks:**
1. ✅ Create template: `templates/public/pronunciation/phoneme-learn.html`
2. ✅ Vue component: PhonemeTheoryViewer
3. ✅ Features:
   - Display IPA symbol + example words
   - Mouth position diagram (upload image)
   - Video embed (YouTube Shorts)
   - Pronunciation tips (Vietnamese explanation)
   - Audio playback (native > TTS fallback)
   - CTA button: "Bắt đầu luyện tập phân biệt âm →"
4. ✅ Add fields to Phoneme model:
   - `mouth_diagram` (ImageField)
   - `video_tutorial_url` (URLField)
   - `pronunciation_tips_vi` (TextField)
   - `tongue_position_description` (TextField)

**Files to create/modify:**
- `backend/apps/curriculum/models/phoneme.py` (add fields)
- `backend/apps/curriculum/migrations/0011_phoneme_learning_content.py`
- `backend/templates/public/pronunciation/phoneme-learn.html`
- `backend/static/js/pronunciation/theory-viewer.js`

**Deliverable:** Learning detail page + migration

---

### **SPRINT 3: DISCRIMINATION PRACTICE (Day 6-7) ⭐ CORE**

#### Day 6: Discrimination UI Component
**Goal:** Build interactive discrimination practice interface

**Tasks:**
1. ✅ Create template: `templates/public/pronunciation/discriminate.html`
2. ✅ Vue component: DiscriminationPractice
3. ✅ Features:
   - Display minimal pair: /i:/ (seat) vs /ɪ/ (sit)
   - Play random audio from one of the pair
   - User clicks which sound they heard
   - Immediate feedback:
     - ✅ Correct: Green highlight + "Chính xác!"
     - ❌ Wrong: Red highlight + Show comparison diagram
   - Progress bar: "7/10 correct"
   - Requirement: 8/10 to unlock production
   - Auto-advance after 10 questions
4. ✅ Comparison modal when wrong:
   - Side-by-side phoneme comparison
   - Tongue position differences
   - Mouth shape differences
   - Audio playback for both

**Files to create:**
- `backend/templates/public/pronunciation/discriminate.html`
- `backend/static/js/pronunciation/discrimination-practice.js`
- `backend/static/css/pronunciation-practice.css`

**Vue.js Structure:**
```javascript
const DiscriminationPractice = {
  data() {
    return {
      phonemeId: null,
      minimalPairs: [],
      currentQuestion: 0,
      correctAnswers: 0,
      totalQuestions: 10,
      isPlaying: false,
      userAnswer: null,
      correctAnswer: null,
      showFeedback: false
    }
  },
  methods: {
    async loadQuiz(),
    async playAudio(phonemeId),
    submitAnswer(answerId),
    showComparison(),
    nextQuestion(),
    finishPractice()
  }
}
```

**Deliverable:** Working discrimination practice component

---

#### Day 7: Discrimination Backend Logic
**Goal:** Quiz generation algorithm + answer validation

**Tasks:**
1. ✅ Create service: `QuizGeneratorService`
   - Select minimal pairs for phoneme
   - Randomize question order
   - Track user history (avoid repeats)
2. ✅ Create service: `DiscriminationScoringService`
   - Calculate accuracy
   - Update UserPhonemeProgress
   - Unlock production stage if accuracy >= 80%
3. ✅ Write comprehensive tests:
   - Test quiz generation (10 unique questions)
   - Test answer validation
   - Test unlock logic
   - Test progress update

**Files to create:**
- `backend/apps/curriculum/services/quiz_generator.py`
- `backend/apps/curriculum/services/scoring_service.py`
- `backend/tests/test_pronunciation/test_quiz_logic.py`

**Deliverable:** Quiz logic + 20 unit tests

---

### **SPRINT 4: PRODUCTION PRACTICE (Day 8-9)**

#### Day 8: Production Practice UI
**Goal:** Audio recording & waveform comparison

**Tasks:**
1. ✅ Create template: `templates/public/pronunciation/practice.html`
2. ✅ Vue component: ProductionPractice
3. ✅ Integrate libraries:
   - **wavesurfer.js** - Waveform visualization
   - **MediaRecorder API** - Audio recording
4. ✅ Features:
   - Show reference waveform (native audio)
   - Record user audio
   - Display user waveform
   - Visual comparison:
     - Duration difference
     - Amplitude pattern
     - Pitch visualization (optional)
   - Retry recording
   - Save best attempt
5. ✅ Feedback system:
   - "Duration: Your audio is 0.2s shorter"
   - "Good attempt! Try to hold the sound longer"
   - No complex AI scoring (Phase 1)

**Files to create:**
- `backend/templates/public/pronunciation/practice.html`
- `backend/static/js/pronunciation/production-practice.js`
- `backend/static/css/waveform-visualizer.css`

**Libraries to add:**
```html
<!-- Waveform visualization -->
<script src="https://unpkg.com/wavesurfer.js@7"></script>
```

**Vue.js Structure:**
```javascript
const ProductionPractice = {
  data() {
    return {
      phonemeId: null,
      referenceAudio: null,
      referenceWaveform: null,
      userWaveform: null,
      mediaRecorder: null,
      isRecording: false,
      audioBlob: null,
      comparisonData: null
    }
  },
  methods: {
    async loadReferenceAudio(),
    initWavesurfer(),
    startRecording(),
    stopRecording(),
    analyzeRecording(),
    saveAttempt(),
    retryRecording()
  }
}
```

**Deliverable:** Working production practice with waveform

---

#### Day 9: Video Mirror & Camera Integration
**Goal:** Add webcam mirroring for mouth shape comparison

**Tasks:**
1. ✅ Integrate WebRTC for camera access
2. ✅ Features:
   - Request camera permission
   - Display user video (mirrored)
   - Display reference video (YouTube embed)
   - Side-by-side comparison
   - Optional: Snapshot comparison
3. ✅ Privacy controls:
   - Camera toggle on/off
   - Video not saved to server
   - Local preview only

**Files to modify:**
- `backend/static/js/pronunciation/production-practice.js`

**Deliverable:** Camera mirroring feature

---

### **SPRINT 5: NAVIGATION & PROGRESS (Day 10)**

#### Day 10: Learning Hub & Progress Dashboard
**Goal:** Central navigation + progress visualization

**Tasks:**
1. ✅ Create hub page: `templates/public/pronunciation/hub.html`
2. ✅ Features:
   - Welcome message
   - Overall progress visualization (Chart.js)
   - 4-stage progress breakdown:
     - ✓ Discovered: 25/44 phonemes
     - 📖 Learning: 12/44 phonemes
     - 🎯 Discriminating: 8/44 phonemes
     - 🎤 Producing: 3/44 phonemes
     - ⭐ Mastered: 2/44 phonemes
   - Quick actions:
     - "Continue where you left off"
     - "Start new phoneme"
     - "Review mastered phonemes"
3. ✅ Progress sidebar component (reusable)
   - Show on all pronunciation pages
   - Current phoneme info
   - Stage indicator
   - Next action button

**Files to create:**
- `backend/templates/public/pronunciation/hub.html`
- `backend/templates/components/_progress_sidebar.html`
- `backend/static/js/pronunciation/progress-dashboard.js`

**Chart.js Integration:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

**Deliverable:** Hub page + progress sidebar

---

## 📁 FILE STRUCTURE (Complete)

```
backend/
├── apps/curriculum/
│   ├── models/
│   │   ├── phoneme.py                    # MODIFY: Add learning content fields
│   │   └── pronunciation.py              # MODIFY: Add stage tracking
│   │
│   ├── migrations/
│   │   ├── 0010_userphonemeprogress_stages.py     # NEW
│   │   └── 0011_phoneme_learning_content.py       # NEW
│   │
│   ├── api/
│   │   └── pronunciation_views.py        # NEW: All 7 endpoints
│   │
│   ├── serializers/
│   │   └── pronunciation_serializers.py  # NEW
│   │
│   ├── services/
│   │   ├── quiz_generator.py             # NEW
│   │   └── scoring_service.py            # NEW
│   │
│   └── urls.py                           # MODIFY: Add routes
│
├── templates/
│   ├── components/
│   │   └── _progress_sidebar.html        # NEW
│   │
│   └── public/pronunciation/
│       ├── hub.html                      # NEW: Learning hub
│       ├── discover.html                 # NEW: Stage 1
│       ├── phoneme-learn.html            # NEW: Stage 2
│       ├── discriminate.html             # NEW: Stage 3
│       └── practice.html                 # NEW: Stage 4
│
├── static/
│   ├── css/
│   │   ├── pronunciation.css             # NEW
│   │   └── waveform-visualizer.css       # NEW
│   │
│   ├── js/pronunciation/
│   │   ├── discovery.js                  # NEW: Vue component
│   │   ├── theory-viewer.js              # NEW: Vue component
│   │   ├── discrimination-practice.js    # NEW: Vue component
│   │   ├── production-practice.js        # NEW: Vue component
│   │   └── progress-dashboard.js         # NEW: Vue component
│   │
│   └── images/phonemes/
│       └── mouth-diagrams/               # NEW: Upload folder
│
└── tests/test_pronunciation/
    ├── test_models.py                    # MODIFY
    ├── test_api_endpoints.py             # NEW
    ├── test_quiz_logic.py                # NEW
    └── test_scoring.py                   # NEW
```

---

## 🎨 DESIGN SYSTEM COMPLIANCE

### Color Usage
```css
/* Stage Indicators */
.stage-discovered { color: var(--primary-blue); }     /* #007BFF */
.stage-learning { color: var(--primary-orange); }     /* #F47C26 */
.stage-discriminating { color: var(--warning); }      /* #FFC107 */
.stage-producing { color: var(--success); }           /* #28A745 */
.stage-mastered { color: #FFD700; }                   /* Gold */

/* Feedback Colors */
.feedback-correct { background: var(--success); }
.feedback-incorrect { background: var(--danger); }
.feedback-neutral { background: var(--info); }
```

### Typography
```css
/* Page Titles */
.pronunciation-title {
  font-family: var(--font-heading);
  font-size: var(--h1);
  color: var(--primary-dark);
  margin-bottom: var(--spacing-lg);
}

/* Phoneme Symbol (IPA) */
.ipa-symbol {
  font-family: 'Doulos SIL', serif;
  font-size: 3rem;
  color: var(--primary-orange);
}

/* Instructions */
.instruction-text {
  font-family: var(--font-body);
  font-size: var(--body);
  color: var(--text-dark);
  line-height: 1.6;
}
```

### Spacing & Layout
```css
/* Card Spacing */
.practice-card {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

/* Grid Layout (Discovery) */
.phoneme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: var(--spacing-md);
}
```

---

## 🧪 TESTING STRATEGY

### Unit Tests (Total: 80+ tests)

#### Model Tests (15 tests)
```python
# test_models.py
def test_user_progress_stage_transitions()
def test_can_practice_discrimination_before_learning()
def test_can_practice_production_only_after_80_percent()
def test_discrimination_accuracy_calculation()
def test_stage_progression_logic()
# ... 10 more
```

#### API Tests (30 tests)
```python
# test_api_endpoints.py
def test_discover_phoneme_creates_progress()
def test_discrimination_quiz_returns_10_questions()
def test_discrimination_submit_correct_answer()
def test_discrimination_submit_wrong_answer()
def test_unlock_production_after_80_percent()
def test_cannot_skip_to_production()
def test_progress_endpoint_aggregates_correctly()
# ... 23 more
```

#### Service Tests (20 tests)
```python
# test_quiz_logic.py
def test_quiz_generator_selects_minimal_pairs()
def test_quiz_avoids_recent_questions()
def test_quiz_randomizes_order()
def test_scoring_calculates_accuracy()
def test_scoring_updates_progress()
# ... 15 more
```

#### Integration Tests (15 tests)
```python
# test_learning_flow.py
def test_complete_learning_journey()
def test_stage_unlocking_sequence()
def test_audio_playback_fallback()
def test_progress_persistence()
# ... 11 more
```

---

## 📊 ACCEPTANCE CRITERIA

### Stage 1: Discovery ✓
- [ ] User can see all 44 phonemes in categorized grid
- [ ] Clicking phoneme plays audio (native > TTS fallback)
- [ ] Discovery is tracked in database
- [ ] Progress badge updates: "Discovered X/44"
- [ ] Responsive on mobile (grid adjusts)

### Stage 2: Learning ✓
- [ ] Phoneme detail page shows:
  - [ ] IPA symbol + example words
  - [ ] Mouth diagram image
  - [ ] Video tutorial (YouTube embed)
  - [ ] Pronunciation tips in Vietnamese
  - [ ] Audio playback button
- [ ] "Start practice" button navigates to Stage 3
- [ ] Page follows design system (colors, typography)

### Stage 3: Discrimination ✓
- [ ] Quiz displays 10 questions
- [ ] Audio plays randomly (one from minimal pair)
- [ ] User clicks correct phoneme
- [ ] Immediate feedback (green/red)
- [ ] Wrong answer shows comparison modal
- [ ] Progress bar updates: "X/10 correct"
- [ ] 8/10 correct unlocks Stage 4
- [ ] Score saved to database

### Stage 4: Production ✓
- [ ] Reference audio displays waveform
- [ ] User can record audio (MediaRecorder)
- [ ] User recording displays waveform
- [ ] Duration comparison shown
- [ ] Retry button works
- [ ] Camera mirror (optional) toggles on/off
- [ ] Best attempt saved

### Navigation ✓
- [ ] Hub page shows overall progress
- [ ] Progress sidebar visible on all pages
- [ ] "Continue learning" button works
- [ ] Breadcrumb navigation shows current stage
- [ ] Cannot skip stages (locked stages grayed out)

### Testing ✓
- [ ] 80+ unit tests pass
- [ ] API tests cover all endpoints
- [ ] Integration tests pass
- [ ] Manual testing checklist completed
- [ ] Mobile responsive verified

---

## 🚀 DEPLOYMENT CHECKLIST

### Database
```bash
# Run migrations
python manage.py makemigrations curriculum
python manage.py migrate

# Create sample data (optional)
python manage.py shell < scripts/seed_phonemes.py
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Tests
```bash
# Run all tests
python manage.py test tests.test_pronunciation -v 2

# Check coverage
coverage run --source='apps/curriculum' manage.py test
coverage report
coverage html
```

### Performance
```bash
# Check query performance
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import override_settings
>>> # Run API calls and check connection.queries
```

---

## 📈 SUCCESS METRICS

### Technical Metrics
- ✅ 80+ unit tests passing
- ✅ API response time < 200ms
- ✅ Frontend load time < 2s
- ✅ Mobile responsive (viewport 320px+)
- ✅ No console errors

### User Experience Metrics
- ✅ User can complete Stage 1-4 without confusion
- ✅ Progress saves correctly across sessions
- ✅ Audio plays without lag
- ✅ Feedback is immediate (<500ms)
- ✅ Camera permission handled gracefully

### Code Quality Metrics
- ✅ PEP 8 compliant
- ✅ ESLint clean (JavaScript)
- ✅ No security vulnerabilities
- ✅ API documentation complete
- ✅ Code comments for complex logic

---

## 🎯 NEXT STEPS AFTER COMPLETION

### Phase 2 Enhancements (Future)
1. AI-powered pronunciation scoring
2. Speech recognition with phoneme detection
3. Gamification: Badges, leaderboards, challenges
4. Social features: Share progress, compete with friends
5. Adaptive learning: AI recommends next phoneme based on weaknesses

### Phase 3 Advanced Features
1. Real-time pronunciation feedback
2. Video recording with playback
3. Native speaker comparison library
4. Accent training (US vs UK vs AU)
5. Minimal pair generator AI

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues

**Issue 1: Audio not playing**
```javascript
// Check AudioContext permission
if (window.AudioContext || window.webkitAudioContext) {
  console.log('Web Audio API supported');
}
```

**Issue 2: Migration conflicts**
```bash
# Reset migrations (dev only)
python manage.py migrate curriculum zero
python manage.py migrate curriculum
```

**Issue 3: Static files not loading**
```bash
# Force collect with clear cache
python manage.py collectstatic --clear --noinput
```

---

## ✅ READY TO START

**Current Status:** All planning complete, ready for implementation

**Start Command:**
```bash
# Create feature branch
git checkout -b feature/pronunciation-learning-flow

# Start Day 1 tasks
# 1. Modify UserPhonemeProgress model
# 2. Create migration
# 3. Write model tests
```

**Estimated Timeline:** 10 working days  
**Team Size:** 1 developer  
**Complexity:** Medium-High  
**Risk Level:** Low (clear requirements, existing foundation)

---

**Last Updated:** 2024-12-16  
**Document Version:** 1.0  
**Status:** 🟢 READY FOR IMPLEMENTATION
