# Days 6-10 Requirements Analysis

**Following:** [DEVELOPMENT_WORKFLOW.md](/DEVELOPMENT_WORKFLOW.md) Phase 1

---

## 📋 PHASE 1: REQUIREMENTS ANALYSIS

### Day 6-7: Discrimination Practice Feature

#### User Stories

**As a learner, I want to:**
1. Practice distinguishing between similar phonemes (minimal pairs)
2. Listen to audio of two phonemes and identify which one matches a target sound
3. Receive immediate feedback on my answers (correct/incorrect)
4. See my accuracy improve over time
5. Focus on phoneme pairs I struggle with

**As the system, I need to:**
- Present random minimal pair questions (e.g., /ɪ/ vs /iː/)
- Play audio samples for comparison
- Track user responses and calculate accuracy
- Store discrimination practice history
- Adjust difficulty based on performance

#### Feature Requirements

**Core Functionality:**
- [ ] Minimal pair quiz interface (A/B comparison)
- [ ] Audio playback for both options
- [ ] Answer submission and validation
- [ ] Real-time feedback (✅ correct / ❌ incorrect)
- [ ] Progress tracking (score, streak, accuracy)
- [ ] Question history and review

**UI Components:**
- Quiz card with question prompt
- Two audio buttons (Option A / Option B)
- Target sound display (IPA + Vietnamese)
- Submit answer button
- Feedback modal (correct/incorrect + explanation)
- Progress bar (e.g., "Question 5/10")
- Score display (current accuracy)

**Data to Track:**
- User's selected answer
- Correct answer
- Response time
- Phoneme pair tested
- Accuracy per session
- Overall discrimination_accuracy per phoneme

#### Edge Cases & Questions

**❓ CLARIFYING QUESTIONS:**

1. **Quiz Structure:**
   - How many questions per session? (Suggest: 10 questions)
   - Should it be timed? (Suggest: No timer, self-paced)
   - Can users skip questions? (Suggest: No, must answer)

2. **Difficulty Levels:**
   - Should we have Easy/Medium/Hard modes?
   - Easy: Very different phonemes (/æ/ vs /ɑː/)
   - Hard: Minimal pairs (/ɪ/ vs /iː/)
   - **Recommendation:** Start with adaptive difficulty (system picks challenging pairs)

3. **Audio Playback:**
   - Can users replay audio unlimited times? (Suggest: Yes)
   - Should we show waveforms? (Suggest: No for discrimination, yes for production)
   - Playback speed control? (Suggest: Phase 2 feature)

4. **Scoring System:**
   - Points per correct answer? (Suggest: 10 points)
   - Streak bonuses? (Suggest: +5 for 3+ correct in a row)
   - Penalties for incorrect? (Suggest: No penalties, educational focus)

5. **Progress Persistence:**
   - Save partial sessions? (Suggest: Yes, allow resume)
   - Show historical performance? (Suggest: Yes, graph in dashboard)

6. **Content Source:**
   - Use existing Phoneme.audio_sample? (Yes)
   - Need separate discrimination audio samples? (Phase 2 if needed)
   - How to generate minimal pairs? (Query MinimalPair model or define in database)

---

### Day 8-9: Production Practice Feature

#### User Stories

**As a learner, I want to:**
1. Record my pronunciation of a phoneme
2. Compare my recording with a native speaker
3. See visual feedback (waveform comparison)
4. Get a score/rating on my pronunciation
5. Re-record if I'm not satisfied
6. Track my production improvement over time

**As the system, I need to:**
- Capture microphone audio in browser
- Upload recordings to server
- (Future) Analyze pronunciation quality
- Store user recordings
- Display waveform visualization
- Track production_best_score

#### Feature Requirements

**Core Functionality:**
- [ ] Microphone permission request
- [ ] Audio recording interface (Record/Stop/Play)
- [ ] Waveform visualization (real-time + playback)
- [ ] Upload recording to server
- [ ] Compare with native speaker audio
- [ ] Basic scoring (phase 1: self-assessment, phase 2: AI analysis)
- [ ] Recording history and playback

**UI Components:**
- Target phoneme display (large IPA symbol)
- Native speaker audio player
- Recording controls (🎤 Record, ⏹️ Stop, ▶️ Play, 🗑️ Delete)
- Waveform canvas (visual feedback)
- Comparison view (native vs user waveforms side-by-side)
- Self-assessment buttons (1-5 stars)
- Submit and save recording

**Technical Considerations:**
- Browser API: `MediaRecorder` API
- Audio format: WebM/Opus (Chrome), MP4/AAC (Safari)
- File size limit: 5MB per recording
- Storage: media/user_recordings/{user_id}/{phoneme_id}/

**Data to Track:**
- Recording file URL
- Duration
- Self-assessment score (1-5)
- Timestamp
- Phoneme practiced
- production_best_score (highest self-assessment)

#### Edge Cases & Questions

**❓ CLARIFYING QUESTIONS:**

1. **Microphone Permission:**
   - How to handle permission denied? (Show instructions, link to settings)
   - Test microphone before recording? (Suggest: Yes, mic check feature)

2. **Recording Limits:**
   - Max recording length? (Suggest: 5 seconds for single phonemes)
   - Max recordings per phoneme? (Suggest: Unlimited, keep best 5)
   - Storage quota per user? (Suggest: 50MB total)

3. **Scoring Method:**
   - Phase 1: Self-assessment only (1-5 stars)?
   - Phase 2: AI pronunciation analysis (future)?
   - **Recommendation:** Start with self-assessment, add AI later

4. **Waveform Visualization:**
   - Library: WaveSurfer.js or custom canvas?
   - **Recommendation:** Use WaveSurfer.js (mature, feature-rich)
   - Show frequency spectrum? (Phase 2 feature)

5. **Audio Comparison:**
   - Side-by-side or overlay waveforms? (Suggest: Side-by-side easier)
   - Play both simultaneously? (Suggest: No, sequential playback)

6. **Recording Storage:**
   - Keep all recordings or only best? (Suggest: Keep all, show best 3)
   - Allow download of recordings? (Suggest: Yes, privacy feature)

7. **Browser Compatibility:**
   - Support Safari (different audio codecs)? (Yes, detect and convert)
   - Mobile recording support? (Yes, responsive design)

---

### Day 10: Learning Hub Dashboard

#### User Stories

**As a learner, I want to:**
1. See my overall pronunciation progress at a glance
2. View statistics (phonemes learned, practice time, accuracy)
3. See charts of my improvement over time
4. Get recommendations on what to practice next
5. Review my recent activity
6. Celebrate achievements (badges, milestones)

**As the system, I need to:**
- Aggregate user progress data
- Calculate statistics (accuracy, time spent, streaks)
- Generate practice recommendations
- Display data visualizations (charts)
- Track learning milestones

#### Feature Requirements

**Core Functionality:**
- [ ] Overview statistics cards (phonemes learned, accuracy, practice time)
- [ ] Progress charts (line chart: accuracy over time)
- [ ] Phoneme mastery breakdown (pie chart or progress bars)
- [ ] Recent activity feed (last 10 practice sessions)
- [ ] Recommended phonemes (based on low accuracy)
- [ ] Achievement badges (milestones)
- [ ] Quick action buttons (Start Practice, Continue Learning)

**UI Components:**
- **Header:** Welcome message + overall score
- **Stats Grid:** 4 cards (Total Phonemes, Mastered, Accuracy, Practice Time)
- **Charts Section:**
  - Line chart: Accuracy trend (last 30 days)
  - Bar chart: Practice frequency per phoneme
- **Recent Activity:** List of recent practice sessions
- **Recommendations:** "You should practice: /ɪ/, /iː/, /æ/"
- **Achievements:** Badge grid (e.g., "First 10 phonemes", "7-day streak")

**Data Sources:**
- UserPhonemeProgress (all phonemes)
- StudySession (practice history)
- Calculated metrics (averages, trends)

**Charts Library:**
- **Recommendation:** Chart.js (lightweight, Vue-compatible)

#### Edge Cases & Questions

**❓ CLARIFYING QUESTIONS:**

1. **Dashboard Sections:**
   - Priority order: Stats → Charts → Activity → Recommendations?
   - Collapsible sections? (Suggest: Fixed layout, scroll)

2. **Statistics Period:**
   - All-time or last 30 days? (Suggest: Toggle between both)
   - Compare with other learners? (Phase 2: leaderboard)

3. **Recommendations Algorithm:**
   - Lowest accuracy first? (Yes)
   - Mix easy and hard phonemes? (Suggest: Focus on weakest 3)
   - Spaced repetition logic? (Phase 2 feature)

4. **Achievements:**
   - What milestones to track? (Suggest: 5, 10, 20, 44 phonemes learned)
   - Display badges? (Yes, visual icons)
   - Notifications? (Phase 2: "You've earned a badge!")

5. **Real-time Updates:**
   - Refresh data on page load or live updates? (Suggest: Refresh on load)
   - WebSocket for live stats? (Phase 2 feature)

---

## 🎯 ACCEPTANCE CRITERIA

### Day 6-7: Discrimination Practice ✅ When:
- [ ] User can start a 10-question discrimination quiz
- [ ] Audio plays correctly for both options (A/B)
- [ ] User selects answer and sees immediate feedback
- [ ] Accuracy is calculated and saved to database
- [ ] Progress bar shows question number (e.g., "5/10")
- [ ] Score updates in real-time
- [ ] Quiz completion shows summary (accuracy, correct answers)
- [ ] UserPhonemeProgress.discrimination_accuracy updates correctly

### Day 8-9: Production Practice ✅ When:
- [ ] User can request microphone permission
- [ ] Recording starts/stops correctly (visual indicator)
- [ ] Waveform displays during recording
- [ ] Playback works for both native and user audio
- [ ] User can self-assess (1-5 stars)
- [ ] Recording uploads to server successfully
- [ ] File is saved in media/user_recordings/
- [ ] UserPhonemeProgress.production_best_score updates
- [ ] User can view recording history (last 5 recordings)

### Day 10: Learning Hub ✅ When:
- [ ] Dashboard loads all user statistics
- [ ] Stats cards show accurate numbers
- [ ] Line chart displays accuracy trend (last 30 days)
- [ ] Bar chart shows practice frequency
- [ ] Recent activity lists last 10 sessions
- [ ] Recommendations show 3 weakest phonemes
- [ ] Achievement badges display earned milestones
- [ ] Quick action buttons navigate correctly
- [ ] Page loads in < 2 seconds
- [ ] Charts are responsive (mobile-friendly)

---

## 📊 TECHNICAL REQUIREMENTS

### Models Needed

**New Models:**
```python
# apps/study/models.py

class DiscriminationAttempt(models.Model):
    """Track individual discrimination quiz attempts"""
    user = ForeignKey(User)
    phoneme_pair = ForeignKey(MinimalPair)  # Or store both phoneme IDs
    phoneme_a = ForeignKey(Phoneme)
    phoneme_b = ForeignKey(Phoneme)
    correct_answer = CharField(choices=['A', 'B'])
    user_answer = CharField(choices=['A', 'B'])
    is_correct = BooleanField()
    response_time = FloatField()  # seconds
    created_at = DateTimeField(auto_now_add=True)

class ProductionRecording(models.Model):
    """Store user pronunciation recordings"""
    user = ForeignKey(User)
    phoneme = ForeignKey(Phoneme)
    recording_file = FileField(upload_to='user_recordings/%Y/%m/')
    duration = FloatField()  # seconds
    self_assessment_score = IntegerField(1-5)  # User's rating
    ai_score = FloatField(null=True)  # Future: AI analysis
    created_at = DateTimeField(auto_now_add=True)
    
class Achievement(models.Model):
    """Define achievement milestones"""
    code = CharField(unique=True)  # e.g., 'first_10_phonemes'
    name = CharField()
    description = TextField()
    icon = CharField()  # Icon class or emoji
    requirement = JSONField()  # Criteria
    
class UserAchievement(models.Model):
    """Track user's earned achievements"""
    user = ForeignKey(User)
    achievement = ForeignKey(Achievement)
    earned_at = DateTimeField(auto_now_add=True)
```

**Existing Models to Update:**
- `UserPhonemeProgress` - Already has discrimination_accuracy, production_best_score ✅
- `MinimalPair` - Check if exists, create if needed

### API Endpoints Needed

**Discrimination:**
- `GET /api/v1/discrimination/start/` - Get quiz questions
- `POST /api/v1/discrimination/submit/` - Submit answer
- `GET /api/v1/discrimination/results/` - Get session results

**Production:**
- `POST /api/v1/production/upload/` - Upload recording
- `GET /api/v1/production/recordings/{phoneme_id}/` - List recordings
- `DELETE /api/v1/production/recordings/{id}/` - Delete recording

**Dashboard:**
- `GET /api/v1/dashboard/stats/` - Overall statistics
- `GET /api/v1/dashboard/chart-data/` - Chart data (accuracy trend)
- `GET /api/v1/dashboard/recommendations/` - Practice suggestions
- `GET /api/v1/dashboard/achievements/` - User achievements

### Frontend Libraries Needed

**Install via CDN (no npm needed):**
- **Chart.js** - For dashboard charts
  ```html
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  ```
  
- **WaveSurfer.js** - For audio waveforms
  ```html
  <script src="https://unpkg.com/wavesurfer.js@7"></script>
  ```

---

## 💰 TIME ESTIMATES

| Feature | Design | Implementation | Testing | Total |
|---------|--------|----------------|---------|-------|
| Discrimination Practice | 2h | 6h | 2h | **10h** |
| Production Practice | 3h | 8h | 3h | **14h** |
| Learning Hub Dashboard | 2h | 5h | 2h | **9h** |
| **TOTAL** | 7h | 19h | 7h | **33h** |

**Breakdown by Day:**
- Day 6: Discrimination design + partial implementation (8h)
- Day 7: Discrimination completion + testing (8h)
- Day 8: Production design + partial implementation (8h)
- Day 9: Production completion + testing (8h)
- Day 10: Dashboard implementation + testing (9h)

---

## 🚀 IMPLEMENTATION ORDER

### Priority 1: Day 6-7 (Discrimination)
1. Check/create MinimalPair model
2. Create DiscriminationAttempt model
3. Implement discrimination quiz API
4. Create quiz UI (Vue.js)
5. Test audio playback and scoring
6. Update UserPhonemeProgress.discrimination_accuracy

### Priority 2: Day 8-9 (Production)
1. Create ProductionRecording model
2. Implement recording upload API
3. Add WaveSurfer.js for waveforms
4. Create recording UI (MediaRecorder)
5. Test recording and playback
6. Update UserPhonemeProgress.production_best_score

### Priority 3: Day 10 (Dashboard)
1. Create Achievement models
2. Implement dashboard statistics API
3. Add Chart.js for visualizations
4. Create dashboard UI
5. Test all charts and data accuracy
6. Performance optimization

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| Browser audio recording compatibility | High | Test on Chrome/Firefox/Safari, provide fallback |
| Large recording file sizes | Medium | Compress audio, set max duration (5s) |
| Chart.js performance with large datasets | Low | Limit data points (30 days max) |
| MinimalPair data not available | High | Generate programmatically or seed from CSV |
| User microphone permission denied | Medium | Clear instructions, graceful degradation |

---

## ❓ FINAL QUESTIONS FOR USER

Before proceeding to Phase 2 (Architecture Design), please confirm:

### 1. Quiz Structure
- **10 questions per discrimination session?** ✅ / ❌
- **No time limit (self-paced)?** ✅ / ❌
- **Must answer all questions (no skip)?** ✅ / ❌

### 2. Recording Feature
- **Self-assessment only (1-5 stars) for now?** ✅ / ❌ (AI scoring is Phase 2)
- **Max 5 seconds per recording?** ✅ / ❌
- **Keep all recordings (show best 3)?** ✅ / ❌

### 3. Dashboard Content
- **Show last 30 days statistics?** ✅ / ❌
- **Recommend top 3 weakest phonemes?** ✅ / ❌
- **Achievement badges (5, 10, 20, 44 phonemes)?** ✅ / ❌

### 4. Priority
- **Implement all 3 features (Days 6-10)?** ✅ / ❌
- **Or focus on 1 feature first?** (Which one?)

### 5. Existing Data
- **Do we have MinimalPair model already?** ✅ / ❌ (I need to check)
- **Do we have sample audio for all 44 phonemes?** ✅ / ❌

---

## 📝 NEXT STEPS

**After user answers questions:**
1. ✅ Move to Phase 2: Architecture Design
2. ✅ Design database models and APIs
3. ✅ Plan URL structure
4. ✅ Verify existing models and data
5. ✅ Create detailed implementation plan

---

**Status:** ⏳ Awaiting user confirmation on questions above  
**Last Updated:** December 16, 2025  
**Phase:** 1 - Requirements Analysis (COMPLETE, pending approval)
