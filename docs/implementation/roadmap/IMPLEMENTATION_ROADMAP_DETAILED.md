# 🗺️ PRONUNCIATION SYSTEM IMPROVEMENT ROADMAP

**Ngày tạo:** 17/12/2025  
**Mục tiêu:** Roadmap chi tiết để đưa hệ thống từ trạng thái hiện tại lên mục tiêu đề ra

---

## 📊 OVERVIEW

### Current State vs Goal

| Tiêu chí | Hiện tại | Mục tiêu | Priority |
|----------|----------|----------|----------|
| **Audio Versioning** | ❌ Không có | ✅ Full versioning | 🔴 Critical |
| **Teacher Dashboard** | ❌ Admin cơ bản | ✅ Smart dashboard | 🔴 Critical |
| **Auto-Generate Pairs** | ❌ Không có | ✅ Script tự động | 🔴 Critical |
| **Discrimination UX** | 🟡 Cơ bản | ✅ Context-rich | 🟠 High |
| **Audio Quality** | 🟡 Mixed | ✅ 100% quality | 🟡 Medium |

### Timeline
- **Phase 1-2 (Week 1-2):** Critical fixes - Audio & Admin
- **Phase 3 (Week 3):** UX improvements
- **Phase 4 (Week 4):** Polish & testing

---

## 🚀 PHASE 1: AUDIO VERSIONING SYSTEM

**Duration:** 1 tuần (5 ngày làm việc)  
**Priority:** 🔴 CRITICAL  
**Goal:** Admin có thể quay lại audio cũ, track versions

### Day 1-2: Database & Model

#### Tasks:
```python
# 1. Create AudioVersion model
- [ ] Write model code (AUDIO_VERSIONING_DESIGN.md)
- [ ] Create migration
- [ ] Test migration on dev DB
- [ ] Write unit tests for model methods

# 2. Migrate existing data
- [ ] Write migration script to convert AudioSource → AudioVersion
- [ ] Test migration với sample data
- [ ] Backup production DB
- [ ] Run migration on staging

# 3. Test model functionality
- [ ] Test activate() method
- [ ] Test version auto-increment
- [ ] Test unique_together constraint
- [ ] Test query performance
```

**Deliverables:**
- ✅ `AudioVersion` model working
- ✅ Existing audio preserved as version 1
- ✅ Unit tests passing

**Testing Checklist:**
```python
# Test cases
def test_create_version():
    """Version number auto-increments"""
    v1 = AudioVersion.objects.create(phoneme=p, audio_source=a1)
    assert v1.version_number == 1
    
    v2 = AudioVersion.objects.create(phoneme=p, audio_source=a2)
    assert v2.version_number == 2

def test_activate_deactivates_others():
    """Activating v2 deactivates v1"""
    v1.activate()
    assert v1.is_active == True
    
    v2.activate()
    assert v2.is_active == True
    
    v1.refresh_from_db()
    assert v1.is_active == False

def test_only_one_active_per_phoneme():
    """Only 1 version can be active"""
    active_count = AudioVersion.objects.filter(
        phoneme=p, is_active=True
    ).count()
    assert active_count == 1
```

---

### Day 3-4: Admin Interface

#### Tasks:
```python
# 1. AudioVersionAdmin
- [ ] Implement AudioVersionAdmin class
- [ ] Add custom displays (badges, audio preview)
- [ ] Add readonly fields (version history table)
- [ ] Add actions (activate, deactivate, compare)
- [ ] Test all admin actions

# 2. Enhanced AudioSourceAdmin
- [ ] Update AudioSourceAdmin to show version info
- [ ] Add link to version history
- [ ] Test navigation between AudioSource ↔ AudioVersion

# 3. Comparison view
- [ ] Create URL for version comparison
- [ ] Create template with side-by-side players
- [ ] Test comparison with 2+ versions
```

**Deliverables:**
- ✅ Admin can view all versions
- ✅ Admin can activate any version (1 click)
- ✅ Admin can compare versions side-by-side
- ✅ Version history clearly visible

**Admin Workflow Test:**
```
1. Login to admin
2. Go to /admin/curriculum/audioversion/
3. Filter by phoneme /p/
4. See list of versions:
   v3 (ACTIVE) - TTS - 90%
   v2 (INACTIVE) - Native - 100%
   v1 (INACTIVE) - TTS - 80%
5. Click "Activate" on v2
6. Confirm v2 is now ACTIVE
7. Go to frontend
8. Play /p/ audio → Should be v2
9. Back to admin
10. Compare v2 vs v3 → See side-by-side players
✅ Pass
```

---

### Day 5: API & Integration

#### Tasks:
```python
# 1. API Endpoints
- [ ] GET /api/v1/audio-versions/<phoneme_id>/
- [ ] POST /api/v1/audio-versions/<version_id>/activate/
- [ ] POST /api/v1/audio-versions/<version_id>/rate/
- [ ] Test all endpoints with Postman

# 2. Frontend Integration
- [ ] Update frontend to fetch active version
- [ ] Handle version changes (cache invalidation)
- [ ] Test audio playback with version switching

# 3. Analytics
- [ ] Track usage_count when audio is played
- [ ] Implement rating system
- [ ] Create analytics dashboard view
```

**Deliverables:**
- ✅ API working
- ✅ Frontend uses correct version
- ✅ Usage tracking functional

**API Test:**
```bash
# Get versions for /p/
curl http://localhost:8000/api/v1/audio-versions/1/

# Response:
{
  "success": true,
  "phoneme": {"id": 1, "ipa_symbol": "p"},
  "versions": [
    {"version_number": 3, "is_active": false, "quality_score": 90},
    {"version_number": 2, "is_active": true, "quality_score": 100},
    {"version_number": 1, "is_active": false, "quality_score": 80}
  ]
}

# Activate version 3
curl -X POST http://localhost:8000/api/v1/audio-versions/3/activate/ \
  -H "Authorization: Token xxx" \
  -d '{"reason": "Testing v3"}'

# Response:
{"success": true, "message": "Version 3 activated"}
```

---

## 🎨 PHASE 2: TEACHER DASHBOARD

**Duration:** 1.5 tuần (7 ngày làm việc)  
**Priority:** 🔴 CRITICAL  
**Goal:** Giáo viên tự quản lý content, không cần dev

### Day 6-7: Setup & Basic Admin

#### Tasks:
```bash
# 1. Install packages
- [ ] pip install django-autocomplete-light==3.9.7
- [ ] pip install django-admin-list-filter-dropdown==1.0.3
- [ ] pip install django-import-export==3.3.1
- [ ] pip install django-admin-sortable2==2.1.9
- [ ] Update requirements.txt
- [ ] Update settings.py
- [ ] Add autocomplete URLs

# 2. Test installation
- [ ] Start dev server
- [ ] Check admin loads
- [ ] Check autocomplete JS works
```

**Deliverables:**
- ✅ Packages installed
- ✅ Settings configured
- ✅ No breaking changes

---

### Day 8-9: Enhanced Admin Interfaces

#### Tasks:
```python
# 1. PhonemeAdmin
- [ ] Implement autocomplete search
- [ ] Add import/export functionality
- [ ] Add custom displays (audio status, pair count)
- [ ] Add filters
- [ ] Test CSV import with sample data

# 2. MinimalPairAdmin
- [ ] Implement autocomplete_fields for phoneme_1, phoneme_2
- [ ] Add custom displays (badges, audio preview)
- [ ] Add bulk actions (generate audio, export Anki)
- [ ] Add data quality check action
- [ ] Test all actions

# 3. Test workflows
- [ ] Create new minimal pair using autocomplete
- [ ] Import CSV with 10 pairs
- [ ] Export Anki flashcards
- [ ] Generate audio for pairs
```

**Deliverables:**
- ✅ Autocomplete working
- ✅ Chọn phoneme < 5 giây (vs 1 phút trước)
- ✅ CSV import/export working
- ✅ Bulk actions working

**Workflow Test:**
```
BEFORE (Hiện tại):
1. Click "Add Minimal Pair"
2. See "Phoneme 1: [Dropdown với 50 IDs]" ❌
3. Guess which ID is /p/ (impossible!)
4. Give up, ask developer

AFTER (Với autocomplete):
1. Click "Add Minimal Pair"
2. Type "p" in "Phoneme 1" field
3. See dropdown: "/p/ - pờ (không có âm ờ)" ✅
4. Click to select
5. Type "b" in "Phoneme 2" field
6. See "/b/ - bờ" ✅
7. Fill words: "Pen" vs "Ben"
8. Save
✅ Total time: 30 seconds (vs impossible before)
```

---

### Day 10-11: Auto-Generate Command

#### Tasks:
```python
# 1. Create management command
- [ ] Write auto_generate_minimal_pairs.py
- [ ] Implement IPA similarity algorithm
- [ ] Implement difficulty calculation
- [ ] Implement difference note generation
- [ ] Test with sample phonemes

# 2. Test scenarios
- [ ] Generate pairs for /p/ vs /b/
- [ ] Generate pairs for /iː/ vs /ɪ/
- [ ] Auto-detect all pairs (--auto)
- [ ] Test with --suggest (no create)
- [ ] Test with different --min-similarity values

# 3. Documentation
- [ ] Write usage guide
- [ ] Add examples
- [ ] Document algorithm
```

**Deliverables:**
- ✅ Command working
- ✅ Can generate 50+ pairs automatically
- ✅ Documentation complete

**Test Run:**
```bash
# Test 1: Specific pair
python manage.py auto_generate_minimal_pairs --phoneme1 p --phoneme2 b

# Expected output:
✅ Found 8 potential minimal pairs:
1. Pen (/pen/) ↔ Ben (/ben/) [0.83]
2. Pat (/pæt/) ↔ Bat (/bæt/) [0.83]
...
✅ Created 8 new minimal pairs!

# Test 2: Auto-detect all
python manage.py auto_generate_minimal_pairs --auto --max-pairs 50

# Expected output:
📊 Analyzing 46 phonemes...
✓ /p/ vs /b/: 8 pairs
✓ /t/ vs /d/: 12 pairs
...
🎯 Top 50 minimal pairs:
1. /iː/ vs /ɪ/: Sheep (/ʃiːp/) ↔ Ship (/ʃɪp/) [0.89]
...
Create these pairs in database? (y/n): y
✅ Created 50 minimal pairs!
```

---

### Day 12: Dashboard Page

#### Tasks:
```python
# 1. Create view
- [ ] Create teacher_dashboard view
- [ ] Calculate statistics
- [ ] Identify phonemes needing attention
- [ ] Test with real data

# 2. Create template
- [ ] Create dashboard template
- [ ] Add stats cards
- [ ] Add action items lists
- [ ] Add quick action buttons
- [ ] Style with CSS

# 3. Test
- [ ] Access dashboard at /admin/teacher-dashboard/
- [ ] Verify all stats are correct
- [ ] Test quick action buttons
- [ ] Test responsive design
```

**Deliverables:**
- ✅ Dashboard accessible
- ✅ Stats accurate
- ✅ Quick actions work
- ✅ UI looks professional

**Dashboard Features:**
```
Stats Cards:
- 📚 46 Phonemes (43 with audio, 40 with native, 38 with 3+ pairs)
- 🔤 87 Minimal Pairs (25 beginner, 42 intermediate, 20 advanced)
- 🎵 156 Audio Files (52 native, 94 TTS, 10 generated)

Action Items:
- ⚠️ 3 phonemes need audio: /ʒ/, /ð/, /ŋ/
- 🔗 8 phonemes need pairs: /ʊ/, /ə/, /ɜː/...

Quick Actions:
- 📚 Manage Phonemes
- 🔤 Manage Minimal Pairs
- 🎵 Manage Audio
- 🔊 Generate Missing Audio (button)
- 🔍 Auto-Find Minimal Pairs (button)
```

---

## 💎 PHASE 3: DISCRIMINATION PAGE REDESIGN

**Duration:** 1 tuần (5 ngày làm việc)  
**Priority:** 🟠 HIGH  
**Goal:** Discrimination page hay như Lesson page

### Day 13-14: Context Phase

#### Tasks:
```html
<!-- 1. Update template -->
- [ ] Add "Context Phase" before quiz
- [ ] Display phoneme comparison cards
- [ ] Show pronunciation tips
- [ ] Show mouth/tongue diagrams
- [ ] Show key differences
- [ ] Show common mistakes

<!-- 2. Create diagrams -->
- [ ] Design mouth position illustrations
- [ ] Create tongue position diagrams
- [ ] Test diagrams on mobile

<!-- 3. Test flow -->
- [ ] User sees context first
- [ ] User reads tips
- [ ] User clicks "Start Quiz"
- [ ] User can return to context anytime
```

**Deliverables:**
- ✅ Context phase implemented
- ✅ Diagrams visible
- ✅ User can navigate back
- ✅ Mobile-friendly

**User Flow:**
```
OLD:
/pronunciation/discrimination/47/
  → [Quiz immediately] ❌

NEW:
/pronunciation/discrimination/47/
  → Phase 1: CONTEXT
     • Phoneme comparison cards
     • Pronunciation tips
     • Diagrams
     • Key differences
     • [Button: Start Quiz]
  
  → Phase 2: QUIZ
     • Questions 1-10
     • [Button: Back to Context]
     • Feedback with explanations
  
  → Phase 3: RESULTS
     • Score
     • [Button: Review Context]
```

---

### Day 15-16: Enhanced Feedback

#### Tasks:
```javascript
// 1. Feedback system
- [ ] Show answer explanation after each question
- [ ] Show pronunciation tip
- [ ] Show phoneme comparison again
- [ ] Play both audios for comparison
- [ ] Test feedback content quality

// 2. Progress indicators
- [ ] Show question number (2/10)
- [ ] Show correct/incorrect count
- [ ] Show progress bar
- [ ] Animate transitions

// 3. Test
- [ ] Answer correctly → See positive feedback
- [ ] Answer incorrectly → See corrective feedback
- [ ] Complete quiz → See detailed results
```

**Deliverables:**
- ✅ Feedback informative
- ✅ User learns from mistakes
- ✅ Progress clear
- ✅ Animations smooth

---

### Day 17: Polish & Testing

#### Tasks:
```
# 1. UI/UX polish
- [ ] Consistent styling with lesson page
- [ ] Loading states
- [ ] Error handling
- [ ] Accessibility (ARIA labels)

# 2. Content quality
- [ ] Review all feedback texts
- [ ] Ensure tips are helpful
- [ ] Check Vietnamese translations
- [ ] Proofread

# 3. Cross-browser testing
- [ ] Test Chrome
- [ ] Test Firefox
- [ ] Test Safari
- [ ] Test mobile browsers
```

**Deliverables:**
- ✅ Professional appearance
- ✅ Content accurate
- ✅ Works on all browsers
- ✅ Accessible

---

## 🎵 PHASE 4: AUDIO QUALITY IMPROVEMENT

**Duration:** 0.5 tuần (2-3 ngày)  
**Priority:** 🟡 MEDIUM  
**Goal:** 100% phoneme có native hoặc high-quality TTS

### Day 18: Audit & Planning

#### Tasks:
```python
# 1. Audio audit
- [ ] List all phonemes
- [ ] Check audio status for each
- [ ] Identify missing audio
- [ ] Identify low-quality audio
- [ ] Create improvement plan

# 2. Quality metrics
- [ ] Define quality criteria
- [ ] Test current audio quality
- [ ] Benchmark native vs TTS
- [ ] Document findings
```

**Deliverables:**
- ✅ Audit report
- ✅ Quality metrics defined
- ✅ Improvement plan

**Audit Report Example:**
```
PHONEME AUDIO AUDIT
===================

Total phonemes: 46

Audio Status:
- ✅ 38 phonemes: Native audio (100% quality)
- 🟡 5 phonemes: TTS only (90% quality)
- ❌ 3 phonemes: No audio

Missing Audio:
1. /ʒ/ - vision
2. /ð/ - this
3. /ŋ/ - sing

TTS Only (need native):
1. /ʊ/ - book
2. /ə/ - about
3. /ɜː/ - bird
4. /ɔː/ - door
5. /ɑː/ - car

Action Plan:
1. Priority 1: Generate TTS for 3 missing (using example words)
2. Priority 2: Record native for 5 TTS-only
3. Priority 3: A/B test best voices
```

---

### Day 19-20: Generate & Upload

#### Tasks:
```python
# 1. Generate missing audio
- [ ] Use generate_phoneme_tts.py script
- [ ] Generate using example words (not IPA symbols)
- [ ] Test quality
- [ ] Upload to AudioSource

# 2. Record native audio (if possible)
- [ ] Contact native speakers
- [ ] Record 5 phonemes
- [ ] Edit/clean audio
- [ ] Upload to AudioSource

# 3. Create versions
- [ ] Create AudioVersion for each new audio
- [ ] Activate best version
- [ ] Test on frontend
```

**Deliverables:**
- ✅ 100% phoneme có audio
- ✅ Audio quality ≥ 90%
- ✅ Users can hear all phonemes

**Script:**
```python
# generate_missing_audio.py

from apps.curriculum.models import Phoneme, AudioSource
from apps.curriculum.services.edge_tts_service import EdgeTTSService

# Get phonemes without audio
phonemes_no_audio = Phoneme.objects.filter(
    preferred_audio_source__isnull=True
)

tts = EdgeTTSService()

for phoneme in phonemes_no_audio:
    # Get example word
    word = phoneme.example_words.first()
    
    if word:
        print(f"Generating audio for /{phoneme.ipa_symbol}/ using '{word.word}'...")
        
        audio_source = tts.generate_phoneme_audio(
            phoneme=phoneme,
            example_word=word.word,
            voice_id='en-US-AriaNeural'
        )
        
        # Create version
        AudioVersion.objects.create(
            phoneme=phoneme,
            audio_source=audio_source,
            change_reason=f"Generated from example word '{word.word}'"
        ).activate()
        
        print(f"✅ Created and activated")
```

---

## ✅ FINAL TESTING & DEPLOYMENT

**Duration:** 2 ngày  
**Priority:** 🔴 CRITICAL

### Day 21: Integration Testing

#### Test Scenarios:
```
Scenario 1: Admin manages audio versions
1. Admin uploads new native audio
2. System creates new version
3. Admin activates new version
4. Users immediately get new audio
✅ Pass

Scenario 2: Teacher creates minimal pairs
1. Teacher opens admin
2. Clicks "Add Minimal Pair"
3. Types "sh" in Phoneme 1 → Sees /ʃ/
4. Types "ch" in Phoneme 2 → Sees /tʃ/
5. Fills words and saves
6. Pair appears in frontend
✅ Pass

Scenario 3: Auto-generate pairs
1. Run: python manage.py auto_generate_minimal_pairs --auto
2. System finds 50 pairs
3. Teacher reviews in admin
4. Teacher activates good ones
5. Students see new pairs in quiz
✅ Pass

Scenario 4: Student learns pronunciation
1. Student opens /pronunciation/discrimination/1/
2. Sees context with tips and diagrams
3. Clicks "Start Quiz"
4. Answers questions
5. Gets feedback with explanations
6. Completes quiz
7. Sees results
✅ Pass
```

---

### Day 22: Deployment

#### Tasks:
```bash
# 1. Backup
- [ ] Backup production database
- [ ] Backup production media files
- [ ] Test backup restore

# 2. Deploy
- [ ] Run migrations on staging
- [ ] Test on staging
- [ ] Deploy to production
- [ ] Run migrations on production
- [ ] Verify production working

# 3. Monitor
- [ ] Check error logs
- [ ] Check performance
- [ ] Get user feedback
```

**Deployment Checklist:**
```
Pre-deployment:
- ✅ All tests passing
- ✅ Code reviewed
- ✅ Database backed up
- ✅ Staging tested

Deployment:
- ✅ Migrations applied
- ✅ Static files collected
- ✅ Cache cleared
- ✅ Server restarted

Post-deployment:
- ✅ Site accessible
- ✅ Admin working
- ✅ Frontend working
- ✅ Audio playing
- ✅ No errors in logs

Monitoring (First 24h):
- ✅ Response times normal
- ✅ No 500 errors
- ✅ Users can complete quizzes
- ✅ Audio versions working
```

---

## 📈 SUCCESS METRICS

### Technical Metrics

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Audio version control | ❌ No | ✅ Yes | To implement |
| Minimal pair creation time | 5 min | 30 sec | To implement |
| Phonemes with audio | 93% | 100% | To implement |
| Admin autocomplete | ❌ No | ✅ Yes | To implement |
| Auto-generate pairs | ❌ No | ✅ Yes | To implement |
| Discrimination UX score | 5/10 | 9/10 | To implement |

### User Impact

**For Teachers:**
- ✅ Tự quản lý content không cần dev
- ✅ Tạo 50 pairs trong 5 phút (vs 4 giờ)
- ✅ Dashboard rõ ràng
- ✅ CSV import/export dễ dàng

**For Students:**
- ✅ Hiểu "tại sao" hai âm khác nhau
- ✅ Context before practice
- ✅ Feedback chi tiết
- ✅ 100% phoneme có audio

**For Admins:**
- ✅ Quay lại audio cũ (1 click)
- ✅ Track version history
- ✅ A/B testing support
- ✅ Analytics dashboard

---

## 🎯 POST-LAUNCH OPTIMIZATION

### Week 5-6: Monitor & Iterate

```
Tasks:
- Monitor user engagement
- Collect feedback
- Analyze quiz completion rate
- Check audio quality ratings
- Identify bottlenecks

Improvements:
- Fine-tune difficulty levels
- Add more minimal pairs
- Improve feedback texts
- Optimize audio loading
```

### Week 7-8: Advanced Features

```
Future enhancements:
- Speech recognition for pronunciation practice
- Waveform visualization
- Video tutorials
- Gamification (badges, streaks)
- Personalized learning paths
```

---

## 📚 DOCUMENTATION

### Required Documentation

```
1. Developer Guide
   - Setup instructions
   - Architecture overview
   - API documentation
   - Database schema

2. Teacher Guide
   - How to use admin
   - How to create minimal pairs
   - How to upload audio
   - How to use dashboard

3. User Guide
   - How to learn pronunciation
   - How to use discrimination quiz
   - Understanding IPA symbols
   - Tips for practice

4. Deployment Guide
   - Server requirements
   - Installation steps
   - Migration guide
   - Troubleshooting
```

---

## 🔗 REFERENCES

- [Gap Analysis](SYSTEM_GAP_ANALYSIS.md)
- [Audio Versioning Design](AUDIO_VERSIONING_DESIGN.md)
- [Teacher Dashboard Design](TEACHER_DASHBOARD_DESIGN.md)
- [Original Roadmap](untitled:Untitled-1)

---

**Tạo bởi:** GitHub Copilot  
**Status:** Ready for execution  
**Next Step:** Begin Phase 1 - Audio Versioning System
