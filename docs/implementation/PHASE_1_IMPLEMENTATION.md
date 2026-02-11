# 🔧 PHASE 1 IMPLEMENTATION - DETAILED EXECUTION GUIDE

**Duration:** Week 1-2 (10 working days)  
**Focus:** Fix TTS + Build Audio Infrastructure  
**Status:** READY TO START

---

## ⚡ QUICK START CHECKLIST

### Before You Start
```bash
# 1. Create feature branch
git checkout -b feature/pronunciation-audio-system

# 2. Create working directory
mkdir -p backend/apps/curriculum/services/
mkdir -p backend/tests/test_pronunciation/
mkdir -p docs/guides/

# 3. Update requirements.txt
# Already has: django, djangorestframework, celery, edge-tts
```

---

## 📊 OVERVIEW

### Problem Statement
**Current Issue:** Edge-TTS attempts to pronounce IPA symbols (e.g., `/i:/`) as literal text, producing incorrect sounds that mislead learners.

**Solution:** Implement a hybrid audio system with intelligent fallback:
1. **Native speaker recordings** (100% accuracy) - PRIMARY
2. **Cached TTS audio** (90% quality, instant) - FALLBACK
3. **On-demand TTS** (80% quality, async) - LAST RESORT
4. **Web Speech API** (browser-based) - FINAL FALLBACK

### Architecture
```
Phoneme
  ├─ audio_sources (1-to-many)
  │   ├─ AudioSource (native, male)
  │   ├─ AudioSource (native, female)
  │   ├─ AudioSource (TTS, Aria)
  │   └─ AudioSource (TTS, Guy)
  └─ preferred_audio_source (FK)

AudioSource
  ├─ phoneme_id (FK)
  ├─ source_type (native|tts|generated)
  ├─ audio_file (FileField)
  ├─ metadata (JSONField)
  └─ cache (1-to-1)
      └─ AudioCache
          ├─ usage_count
          ├─ file_size
          └─ generated_at
```

---

## 📝 WEEK 1: MODEL & INFRASTRUCTURE SETUP

### Day 1-2: Database Models

See detailed guide: [PHASE_1_DAY_1_EXECUTION.md](./PHASE_1_DAY_1_EXECUTION.md)

**Tasks:**
- Create `AudioSource` model
- Create `AudioCache` model
- Update `Phoneme` model with audio reference
- Write and apply migrations
- Unit tests for models

**Deliverables:**
- ✅ Migration files (0008, 0009)
- ✅ Model classes with full docstrings
- ✅ 10+ unit tests passing

### Day 3-4: Service Layer

**File:** `backend/apps/curriculum/services/audio_service.py`

**Key Components:**
```python
class PhonemeAudioService:
    """
    Central audio management service.
    
    Features:
    - Intelligent fallback (native → TTS → on-demand)
    - Django cache integration (30-day TTL)
    - Usage tracking and analytics
    - Async TTS generation support
    """
    
    @staticmethod
    def get_phoneme_audio(phoneme_id, force_refresh=False):
        """Get audio with fallback strategy."""
        pass
    
    @staticmethod
    def get_audio_with_fallback(phoneme_id):
        """Get audio or return Web Speech API fallback."""
        pass
    
    @staticmethod
    def clear_phoneme_cache(phoneme_id):
        """Clear cache for specific phoneme."""
        pass
```

**Testing:**
- Service unit tests
- Cache hit/miss scenarios
- Fallback logic verification

### Day 5: Admin Integration

**File:** `backend/apps/curriculum/admin.py`

**Features:**
- Register `AudioSource` and `AudioCache` in Django admin
- Bulk actions for TTS generation
- Filtering by source type, voice ID
- Audio preview in admin list view

**Admin Actions:**
```python
actions = [
    'generate_missing_tts',
    'regenerate_tts',
    'clear_cache',
]
```

---

## 🧪 WEEK 2: TESTING & INTEGRATION

### Day 1-2: API Integration

**File:** `backend/apps/curriculum/views_pronunciation.py`

Update `PronunciationLessonDetailView` to include audio URLs:

```python
class PronunciationLessonDetailView(APIView):
    def get(self, request, slug):
        lesson = get_object_or_404(PronunciationLesson, slug=slug)
        phonemes = lesson.phonemes.all()
        
        phonemes_data = []
        for phoneme in phonemes:
            audio = PhonemeAudioService.get_audio_with_fallback(phoneme.id)
            phonemes_data.append({
                'id': phoneme.id,
                'ipa_symbol': phoneme.ipa_symbol,
                'audio': {
                    'source_type': audio['source_type'],
                    'url': audio['audio_url'],
                    'fallback_text': audio.get('fallback_text'),
                },
            })
        
        return Response({'phonemes': phonemes_data})
```

### Day 3-4: Frontend Integration

**File:** `backend/templates/pages/pronunciation_lesson.html`

Update Vue.js `playPhoneme()` method:

```javascript
async playPhoneme(phoneme) {
    this.isPlaying = true;
    
    try {
        // Use native/cached audio if available
        if (phoneme.audio && phoneme.audio.url) {
            const audio = new Audio(phoneme.audio.url);
            await audio.play();
            
            audio.onended = () => {
                this.isPlaying = false;
            };
        } else if (phoneme.audio && phoneme.audio.fallback_text) {
            // Fallback to Web Speech API
            const utterance = new SpeechSynthesisUtterance(
                phoneme.audio.fallback_text
            );
            utterance.lang = 'en-US';
            speechSynthesis.speak(utterance);
            
            utterance.onend = () => {
                this.isPlaying = false;
            };
        }
    } catch (error) {
        console.error('Audio playback failed:', error);
        this.isPlaying = false;
    }
}
```

### Day 5: Quality Assurance

**Testing Checklist:**
```
[ ] Unit tests: All models, services pass
[ ] Integration tests: API returns correct audio URLs
[ ] E2E tests: Frontend plays audio correctly
[ ] Mobile tests: Audio works on iOS/Android
[ ] Performance: Cache hit rate >80%
[ ] Accessibility: Screen reader announces audio quality
```

---

## 📦 DELIVERABLES

### Code Files
- ✅ `backend/apps/curriculum/models.py` (updated with AudioSource, AudioCache)
- ✅ `backend/apps/curriculum/services/audio_service.py` (new)
- ✅ `backend/apps/curriculum/migrations/0008_audiosource.py` (new)
- ✅ `backend/apps/curriculum/migrations/0009_phoneme_audio_update.py` (new)
- ✅ `backend/apps/curriculum/admin.py` (updated)
- ✅ `backend/apps/curriculum/views_pronunciation.py` (updated)
- ✅ `backend/templates/pages/pronunciation_lesson.html` (updated)
- ✅ `backend/tests/test_pronunciation/test_audio_service.py` (new)

### Documentation
- ✅ Phase 1 implementation guide (this file)
- ✅ API documentation updates
- ✅ Admin user guide
- ✅ Architecture diagrams

### Database
- ✅ `curriculum_audiosource` table
- ✅ `curriculum_audiocache` table
- ✅ Indexes for performance
- ✅ Foreign key constraints

---

## 🎯 SUCCESS METRICS

- **Audio Quality:** 100% of phonemes have native or high-quality TTS
- **Performance:** <100ms audio load time (cached)
- **Reliability:** <1% audio playback errors
- **Coverage:** 100% of phonemes have at least one audio source
- **User Experience:** Smooth playback, no delays

---

## 🚀 NEXT STEPS

**After Phase 1 completion:**
- **Phase 2:** Visual mouth mechanics (SVG diagrams)
- **Phase 3:** Progressive difficulty paths (3-level system)
- **Phase 4:** Speaking practice (recording + AI feedback)
- **Phase 5:** Teacher dashboard (content management)

---

**Ready to start?** See [PHASE_1_DAY_1_EXECUTION.md](./PHASE_1_DAY_1_EXECUTION.md) for step-by-step Day 1 guide.