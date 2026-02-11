# Days 6-10 UI/UX Design

**Following:** [DEVELOPMENT_WORKFLOW.md](/DEVELOPMENT_WORKFLOW.md) Phase 3  
**Architecture:** [DAYS_6_10_ARCHITECTURE.md](/DAYS_6_10_ARCHITECTURE.md)

---

## 🎨 DESIGN SYSTEM REFERENCE

### Color Palette (Existing - MUST USE)

```css
/* Primary Colors */
--primary-orange: #F47C26        /* Main CTA buttons */
--primary-orange-hover: #E06B1F  /* Hover states */
--primary-dark: #183B56          /* Headers, dark text */

/* Status Colors */
--success: #28A745               /* Correct answers, achievements */
--danger: #DC3545                /* Wrong answers, errors */
--warning: #FFC107               /* Warnings, timers */
--info: #17A2B8                  /* Info messages */

/* Backgrounds */
--bg-body: #F9FAFC               /* Page background */
--bg-white: #FFFFFF              /* Cards, panels */
--bg-light: #F8F9FA              /* Subtle backgrounds */
```

### Typography

```css
--font-heading: 'Montserrat'     /* Headers */
--font-body: 'Open Sans'         /* Body text */

--fs-xs: 0.75rem    (12px)
--fs-sm: 0.875rem   (14px)
--fs-base: 1rem     (16px)
--fs-lg: 1.25rem    (20px)
--fs-xl: 1.5rem     (24px)
--fs-2xl: 2rem      (32px)
--fs-3xl: 2.5rem    (40px)
```

### Spacing & Borders

```css
--spacing-sm: 0.5rem   (8px)
--spacing-md: 1rem     (16px)
--spacing-lg: 1.5rem   (24px)
--spacing-xl: 2rem     (32px)

--radius-md: 8px
--radius-lg: 12px
--radius-xl: 16px

--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12)
```

---

## 📱 DAY 6-7: DISCRIMINATION PRACTICE UI

### Page 1: Quiz Start Screen

**URL:** `/discrimination/start/`

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Header: Logo + User Menu                   │
├─────────────────────────────────────────────┤
│                                             │
│         🎯 Phoneme Discrimination Quiz      │
│                                             │
│   Test your ability to distinguish between  │
│   similar English sounds                    │
│                                             │
│   ┌───────────────────────────────────┐   │
│   │ 📊 Quiz Details                   │   │
│   │                                   │   │
│   │ • 10 Questions                    │   │
│   │ • 5 Minutes Time Limit            │   │
│   │ • Focus: Minimal Pairs            │   │
│   │ • Difficulty: Adaptive            │   │
│   └───────────────────────────────────┘   │
│                                             │
│   ┌───────────────────────────────────┐   │
│   │ 📈 Your Stats                     │   │
│   │                                   │   │
│   │ Best Score: 85%                   │   │
│   │ Sessions Completed: 12            │   │
│   │ Avg Response Time: 4.2s           │   │
│   └───────────────────────────────────┘   │
│                                             │
│         [Start Quiz] (Orange Button)        │
│         [View History] (Secondary)          │
│                                             │
└─────────────────────────────────────────────┘
```

**Component Breakdown:**

**1. Hero Section**
```html
<div class="quiz-hero">
    <div class="icon-circle">🎯</div>
    <h1>Phoneme Discrimination Quiz</h1>
    <p class="subtitle">Test your ability to distinguish between similar English sounds</p>
</div>

<style>
.quiz-hero {
    text-align: center;
    padding: var(--spacing-2xl) var(--spacing-xl);
}

.icon-circle {
    width: 80px;
    height: 80px;
    background: var(--primary-orange-light);
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--fs-3xl);
    margin: 0 auto var(--spacing-lg);
}

.quiz-hero h1 {
    font-family: var(--font-heading);
    font-size: var(--fs-2xl);
    color: var(--primary-dark);
    margin-bottom: var(--spacing-sm);
}

.subtitle {
    color: var(--text-muted);
    font-size: var(--fs-md);
}
</style>
```

**2. Info Cards (2 columns)**
```html
<div class="info-cards">
    <div class="info-card">
        <h3>📊 Quiz Details</h3>
        <ul class="details-list">
            <li>• 10 Questions</li>
            <li>• 5 Minutes Time Limit</li>
            <li>• Focus: Minimal Pairs</li>
            <li>• Difficulty: Adaptive</li>
        </ul>
    </div>
    
    <div class="info-card">
        <h3>📈 Your Stats</h3>
        <div class="stat-row">
            <span>Best Score:</span>
            <strong>85%</strong>
        </div>
        <div class="stat-row">
            <span>Sessions Completed:</span>
            <strong>12</strong>
        </div>
        <div class="stat-row">
            <span>Avg Response Time:</span>
            <strong>4.2s</strong>
        </div>
    </div>
</div>

<style>
.info-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
    margin: var(--spacing-xl) 0;
}

.info-card {
    background: var(--bg-white);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    box-shadow: var(--shadow-md);
}

.info-card h3 {
    font-size: var(--fs-lg);
    margin-bottom: var(--spacing-md);
    color: var(--primary-dark);
}

.details-list {
    list-style: none;
    padding: 0;
}

.details-list li {
    padding: var(--spacing-sm) 0;
    color: var(--text-body);
}

.stat-row {
    display: flex;
    justify-content: space-between;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--border-light);
}

.stat-row:last-child {
    border-bottom: none;
}
</style>
```

**3. Action Buttons**
```html
<div class="actions">
    <button class="btn btn-primary btn-lg" @click="startQuiz">
        Start Quiz
    </button>
    <button class="btn btn-secondary btn-lg" @click="viewHistory">
        View History
    </button>
</div>

<style>
.actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    margin-top: var(--spacing-xl);
}

.btn {
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: var(--radius-md);
    font-weight: var(--fw-semibold);
    transition: var(--transition-fast);
    border: none;
    cursor: pointer;
    font-size: var(--fs-base);
}

.btn-primary {
    background: var(--primary-orange);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-orange-hover);
    box-shadow: var(--shadow-orange);
    transform: translateY(-2px);
}

.btn-secondary {
    background: var(--bg-light);
    color: var(--primary-dark);
    border: 1px solid var(--border-color);
}

.btn-lg {
    font-size: var(--fs-md);
    padding: var(--spacing-md) var(--spacing-2xl);
}
</style>
```

---

### Page 2: Quiz Interface (Active Quiz)

**URL:** `/discrimination/quiz/{session_id}/`

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Progress: [■■■■■□□□□□] 5/10   ⏱️ 2:30     │
├─────────────────────────────────────────────┤
│                                             │
│   Question 5 of 10                          │
│   ────────────────                          │
│                                             │
│   Which word did you hear?                  │
│                                             │
│   🔊 [Play Target Sound]                    │
│                                             │
│   Choose the correct word:                  │
│                                             │
│   ┌─────────────────┐  ┌─────────────────┐│
│   │  Option A       │  │  Option B       ││
│   │                 │  │                 ││
│   │  🔊 ship       │  │  🔊 sheep      ││
│   │  /ʃɪp/         │  │  /ʃiːp/        ││
│   │  (tàu)         │  │  (cừu)         ││
│   │                 │  │                 ││
│   │  [Select]      │  │  [Select]      ││
│   └─────────────────┘  └─────────────────┘│
│                                             │
│   ⚠️ Selected: Option A                     │
│                                             │
│   [Submit Answer] (Disabled until selected) │
│                                             │
│   Score: 4/5 (80%)                          │
│                                             │
└─────────────────────────────────────────────┘
```

**Component Breakdown:**

**1. Progress Header (Fixed Top)**
```html
<div class="quiz-header">
    <div class="progress-section">
        <div class="progress-bar">
            <div class="progress-fill" :style="{width: progressPercent + '%'}"></div>
        </div>
        <span class="progress-text">[[ questionNumber ]]/10</span>
    </div>
    
    <div class="timer" :class="{warning: timeRemaining < 60}">
        ⏱️ [[ formatTime(timeRemaining) ]]
    </div>
    
    <div class="score">
        Score: [[ correctAnswers ]]/[[ questionNumber - 1 ]] ([[ accuracy ]]%)
    </div>
</div>

<style>
.quiz-header {
    position: sticky;
    top: 0;
    background: var(--bg-white);
    padding: var(--spacing-md);
    box-shadow: var(--shadow-sm);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 100;
    gap: var(--spacing-lg);
}

.progress-section {
    flex: 1;
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.progress-bar {
    flex: 1;
    height: 8px;
    background: var(--bg-light);
    border-radius: var(--radius-full);
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--primary-orange);
    transition: width var(--transition-normal);
}

.progress-text {
    font-weight: var(--fw-semibold);
    color: var(--primary-dark);
    min-width: 50px;
}

.timer {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-weight: var(--fw-semibold);
    color: var(--text-body);
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--bg-light);
    border-radius: var(--radius-md);
}

.timer.warning {
    background: var(--warning-light);
    color: var(--warning);
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.score {
    font-weight: var(--fw-semibold);
    color: var(--primary-dark);
}
</style>
```

**2. Question Card**
```html
<div class="question-container">
    <div class="question-header">
        <span class="question-number">Question [[ questionNumber ]] of 10</span>
        <span class="difficulty-badge">[[ difficulty ]]</span>
    </div>
    
    <h2 class="question-text">Which word did you hear?</h2>
    
    <div class="target-audio">
        <button class="btn-audio-large" @click="playTargetAudio">
            🔊 Play Target Sound
        </button>
        <p class="hint">Listen carefully and choose the matching word below</p>
    </div>
</div>

<style>
.question-container {
    max-width: 700px;
    margin: var(--spacing-2xl) auto;
    padding: 0 var(--spacing-lg);
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
}

.question-number {
    font-size: var(--fs-sm);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.difficulty-badge {
    font-size: var(--fs-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--info-light);
    color: var(--info);
    border-radius: var(--radius-sm);
    font-weight: var(--fw-semibold);
}

.question-text {
    font-size: var(--fs-xl);
    color: var(--primary-dark);
    margin-bottom: var(--spacing-xl);
    font-weight: var(--fw-semibold);
}

.target-audio {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
}

.btn-audio-large {
    background: var(--primary-orange);
    color: white;
    border: none;
    padding: var(--spacing-lg) var(--spacing-2xl);
    border-radius: var(--radius-lg);
    font-size: var(--fs-lg);
    font-weight: var(--fw-semibold);
    cursor: pointer;
    transition: var(--transition-fast);
    box-shadow: var(--shadow-md);
}

.btn-audio-large:hover {
    background: var(--primary-orange-hover);
    transform: scale(1.05);
    box-shadow: var(--shadow-orange);
}

.btn-audio-large:active {
    transform: scale(0.98);
}

.hint {
    margin-top: var(--spacing-md);
    color: var(--text-muted);
    font-size: var(--fs-sm);
}
</style>
```

**3. Answer Options (2 Cards Side-by-Side)**
```html
<div class="options-grid">
    <div 
        class="option-card" 
        :class="{selected: selectedOption === 'word_1'}"
        @click="selectOption('word_1')"
    >
        <div class="option-label">Option A</div>
        
        <button class="btn-audio-option" @click.stop="playAudio('word_1')">
            🔊
        </button>
        
        <div class="word-display">
            <h3 class="word">[[ currentQuestion.word_1 ]]</h3>
            <p class="ipa">[[ currentQuestion.word_1_ipa ]]</p>
            <p class="meaning">([[ currentQuestion.word_1_meaning ]])</p>
        </div>
        
        <div class="select-indicator">
            <span v-if="selectedOption === 'word_1'">✓ Selected</span>
        </div>
    </div>
    
    <div 
        class="option-card" 
        :class="{selected: selectedOption === 'word_2'}"
        @click="selectOption('word_2')"
    >
        <!-- Similar structure for Option B -->
    </div>
</div>

<style>
.options-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

@media (max-width: 768px) {
    .options-grid {
        grid-template-columns: 1fr;
    }
}

.option-card {
    background: var(--bg-white);
    border: 2px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    cursor: pointer;
    transition: var(--transition-fast);
    position: relative;
}

.option-card:hover {
    border-color: var(--primary-orange);
    box-shadow: var(--shadow-md);
    transform: translateY(-4px);
}

.option-card.selected {
    border-color: var(--primary-orange);
    background: var(--primary-orange-light);
    box-shadow: var(--shadow-orange);
}

.option-label {
    position: absolute;
    top: var(--spacing-sm);
    left: var(--spacing-sm);
    font-size: var(--fs-xs);
    font-weight: var(--fw-semibold);
    color: var(--text-muted);
    text-transform: uppercase;
}

.btn-audio-option {
    width: 60px;
    height: 60px;
    background: var(--bg-light);
    border: none;
    border-radius: var(--radius-full);
    font-size: var(--fs-2xl);
    cursor: pointer;
    transition: var(--transition-fast);
    margin: var(--spacing-lg) auto;
    display: block;
}

.btn-audio-option:hover {
    background: var(--primary-orange-light);
    transform: scale(1.1);
}

.word-display {
    text-align: center;
    margin-top: var(--spacing-md);
}

.word {
    font-size: var(--fs-2xl);
    font-weight: var(--fw-bold);
    color: var(--primary-dark);
    margin-bottom: var(--spacing-sm);
}

.ipa {
    font-size: var(--fs-lg);
    color: var(--primary-orange);
    font-weight: var(--fw-medium);
    margin-bottom: var(--spacing-xs);
}

.meaning {
    font-size: var(--fs-sm);
    color: var(--text-muted);
}

.select-indicator {
    text-align: center;
    margin-top: var(--spacing-md);
    min-height: 24px;
}

.select-indicator span {
    color: var(--success);
    font-weight: var(--fw-semibold);
    font-size: var(--fs-sm);
}
</style>
```

**4. Submit Button**
```html
<div class="submit-section">
    <div v-if="selectedOption" class="selection-preview">
        ⚠️ You selected: <strong>[[ selectedOption === 'word_1' ? 'Option A' : 'Option B' ]]</strong>
    </div>
    
    <button 
        class="btn btn-primary btn-submit"
        :disabled="!selectedOption"
        @click="submitAnswer"
    >
        Submit Answer
    </button>
</div>

<style>
.submit-section {
    text-align: center;
    margin-top: var(--spacing-xl);
}

.selection-preview {
    margin-bottom: var(--spacing-md);
    color: var(--text-body);
    font-size: var(--fs-base);
}

.btn-submit {
    min-width: 200px;
    padding: var(--spacing-md) var(--spacing-2xl);
    font-size: var(--fs-md);
}

.btn-submit:disabled {
    background: var(--bg-light);
    color: var(--text-muted);
    cursor: not-allowed;
    box-shadow: none;
}
</style>
```

**5. Feedback Modal (After Submit)**
```html
<div class="modal-overlay" v-if="showFeedback" @click="closeFeedback">
    <div class="modal-content feedback-modal" @click.stop>
        <div class="feedback-header" :class="feedbackClass">
            <div class="feedback-icon">
                [[ isCorrect ? '✅' : '❌' ]]
            </div>
            <h3>[[ isCorrect ? 'Correct!' : 'Incorrect' ]]</h3>
        </div>
        
        <div class="feedback-body">
            <p class="feedback-message">[[ feedbackMessage ]]</p>
            
            <div class="answer-comparison">
                <div class="answer-row">
                    <span class="label">Correct Answer:</span>
                    <strong>[[ correctAnswer ]]</strong>
                </div>
                <div class="answer-row">
                    <span class="label">Your Answer:</span>
                    <strong>[[ userAnswer ]]</strong>
                </div>
            </div>
            
            <div class="phoneme-explanation">
                <h4>💡 Key Difference:</h4>
                <p>[[ explanationText ]]</p>
            </div>
        </div>
        
        <div class="feedback-actions">
            <button class="btn btn-primary" @click="nextQuestion">
                [[ questionNumber < 10 ? 'Next Question' : 'View Results' ]] →
            </button>
        </div>
    </div>
</div>

<style>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn var(--transition-fast);
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.modal-content {
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
    animation: slideUp var(--transition-normal);
}

@keyframes slideUp {
    from {
        transform: translateY(30px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.feedback-header {
    padding: var(--spacing-xl);
    text-align: center;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}

.feedback-header.correct {
    background: var(--success-light);
}

.feedback-header.incorrect {
    background: var(--danger-light);
}

.feedback-icon {
    font-size: var(--fs-4xl);
    margin-bottom: var(--spacing-md);
}

.feedback-header h3 {
    font-size: var(--fs-xl);
    color: var(--primary-dark);
}

.feedback-body {
    padding: var(--spacing-xl);
}

.feedback-message {
    font-size: var(--fs-md);
    color: var(--text-body);
    margin-bottom: var(--spacing-lg);
}

.answer-comparison {
    background: var(--bg-light);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.answer-row {
    display: flex;
    justify-content: space-between;
    padding: var(--spacing-sm) 0;
}

.phoneme-explanation {
    background: var(--info-light);
    border-left: 4px solid var(--info);
    padding: var(--spacing-md);
    border-radius: var(--radius-sm);
}

.phoneme-explanation h4 {
    font-size: var(--fs-base);
    margin-bottom: var(--spacing-sm);
    color: var(--primary-dark);
}

.feedback-actions {
    padding: var(--spacing-lg) var(--spacing-xl);
    border-top: 1px solid var(--border-light);
}

.feedback-actions .btn {
    width: 100%;
}
</style>
```

---

### Page 3: Quiz Results

**URL:** `/discrimination/results/{session_id}/`

**Layout:**
```
┌─────────────────────────────────────────────┐
│            Quiz Complete! 🎉                │
│                                             │
│   ┌─────────────────────────────────────┐ │
│   │  Final Score                        │ │
│   │                                     │ │
│   │       80%                           │ │
│   │      8/10 correct                   │ │
│   └─────────────────────────────────────┘ │
│                                             │
│   ┌────────────┬────────────┬────────────┐│
│   │ Accuracy   │ Time Spent │ Avg Time   ││
│   │    80%     │   3:24     │   20.4s    ││
│   └────────────┴────────────┴────────────┘│
│                                             │
│   Performance Breakdown:                    │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                             │
│   [Q1] ✅ ship vs sheep - 3.2s             │
│   [Q2] ✅ sit vs seat - 2.8s               │
│   [Q3] ❌ bat vs bad - 5.1s                │
│   ...                                       │
│                                             │
│   [Try Again] [View Dashboard] [Home]       │
└─────────────────────────────────────────────┘
```

(Continued in next section...)

---

## 📱 DAY 8-9: PRODUCTION PRACTICE UI

### Page 1: Recording Interface

**URL:** `/production/phoneme/{phoneme_id}/`

**Layout:**
```
┌─────────────────────────────────────────────┐
│  ← Back to Phonemes                         │
├─────────────────────────────────────────────┤
│                                             │
│   Practice Pronunciation: /ɪ/               │
│   ───────────────────────────                │
│                                             │
│   ┌──────────────────────────────────────┐ │
│   │  🔊 Native Speaker                   │ │
│   │                                      │ │
│   │  ▶️ [Play]                           │ │
│   │  [Waveform Visualization]            │ │
│   │                                      │ │
│   │  Listen to the correct pronunciation │ │
│   └──────────────────────────────────────┘ │
│                                             │
│   ┌──────────────────────────────────────┐ │
│   │  🎤 Your Recording                   │ │
│   │                                      │ │
│   │  [●  Record]  [⏹  Stop]  [▶️  Play] │ │
│   │  [Waveform Visualization]            │ │
│   │                                      │ │
│   │  Duration: 2.3s                      │ │
│   │                                      │ │
│   │  Rate your pronunciation:            │ │
│   │  ⭐⭐⭐⭐☆                             │ │
│   │                                      │ │
│   │  [Save Recording]  [Try Again]       │ │
│   └──────────────────────────────────────┘ │
│                                             │
│   Previous Recordings (Best 3):             │
│   ┌────────┬────────┬────────┐            │
│   │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐⭐☆ │ ⭐⭐⭐☆☆ │            │
│   │ 2.1s   │ 2.5s   │ 3.0s   │            │
│   │ [Play] │ [Play] │ [Play] │            │
│   └────────┴────────┴────────┘            │
│                                             │
└─────────────────────────────────────────────┘
```

**Component Breakdown:**

**1. Header Section**
```html
<div class="practice-header">
    <a href="/pronunciation/discovery/" class="back-link">
        ← Back to Phonemes
    </a>
    
    <div class="phoneme-title">
        <h1>Practice Pronunciation</h1>
        <div class="phoneme-display">
            <span class="ipa-large">/[[ phoneme.ipa_symbol ]]/</span>
            <span class="phoneme-name">[[ phoneme.name_vi ]]</span>
        </div>
    </div>
</div>

<style>
.practice-header {
    margin-bottom: var(--spacing-xl);
}

.back-link {
    color: var(--primary-orange);
    text-decoration: none;
    font-weight: var(--fw-medium);
    display: inline-flex;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.phoneme-title {
    text-align: center;
}

.phoneme-display {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-lg);
    margin-top: var(--spacing-md);
}

.ipa-large {
    font-size: var(--fs-4xl);
    font-weight: var(--fw-bold);
    color: var(--primary-orange);
}

.phoneme-name {
    font-size: var(--fs-lg);
    color: var(--text-muted);
}
</style>
```

**2. Native Speaker Audio Section**
```html
<div class="audio-section native-section">
    <h3>🔊 Native Speaker</h3>
    
    <div class="audio-controls">
        <button class="btn-audio-control" @click="playNativeAudio">
            <span v-if="!nativeIsPlaying">▶️ Play</span>
            <span v-else>⏸️ Pause</span>
        </button>
        
        <div class="audio-info">
            <span class="duration">[[ nativeDuration ]]s</span>
        </div>
    </div>
    
    <div id="native-waveform" class="waveform-container"></div>
    
    <p class="hint">Listen carefully to the native pronunciation</p>
</div>

<style>
.audio-section {
    background: var(--bg-white);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
    box-shadow: var(--shadow-md);
}

.audio-section h3 {
    font-size: var(--fs-lg);
    color: var(--primary-dark);
    margin-bottom: var(--spacing-lg);
}

.audio-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
}

.btn-audio-control {
    background: var(--primary-orange);
    color: white;
    border: none;
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: var(--radius-md);
    font-size: var(--fs-base);
    font-weight: var(--fw-semibold);
    cursor: pointer;
    transition: var(--transition-fast);
    min-width: 120px;
}

.btn-audio-control:hover {
    background: var(--primary-orange-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.audio-info {
    color: var(--text-muted);
    font-size: var(--fs-sm);
}

.waveform-container {
    background: var(--bg-light);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    min-height: 80px;
}

.hint {
    text-align: center;
    color: var(--text-muted);
    font-size: var(--fs-sm);
    font-style: italic;
}
</style>
```

**3. Recording Section**
```html
<div class="audio-section recording-section">
    <h3>🎤 Your Recording</h3>
    
    <!-- Microphone Permission Request -->
    <div v-if="!micPermissionGranted" class="mic-permission">
        <p>We need access to your microphone to record your pronunciation.</p>
        <button class="btn btn-primary" @click="requestMicPermission">
            🎤 Grant Microphone Access
        </button>
    </div>
    
    <!-- Recording Controls -->
    <div v-else class="recording-controls">
        <button 
            class="btn-record" 
            :class="{recording: isRecording}"
            @click="toggleRecording"
            :disabled="isPlaying"
        >
            <span v-if="!isRecording">● Record</span>
            <span v-else>⏹ Stop</span>
        </button>
        
        <button 
            class="btn-play"
            @click="playRecording"
            :disabled="!hasRecording || isRecording"
        >
            ▶️ Play
        </button>
        
        <button 
            class="btn-delete"
            @click="deleteRecording"
            :disabled="!hasRecording || isRecording"
        >
            🗑️ Delete
        </button>
        
        <div class="recording-timer" v-if="isRecording">
            ⏺️ [[ recordingTime ]]s / 5s
        </div>
    </div>
    
    <div id="user-waveform" class="waveform-container"></div>
    
    <div v-if="hasRecording" class="recording-info">
        <span>Duration: [[ recordingDuration ]]s</span>
    </div>
    
    <!-- Self-Assessment -->
    <div v-if="hasRecording" class="self-assessment">
        <h4>Rate your pronunciation:</h4>
        <div class="star-rating">
            <span 
                v-for="star in 5" 
                :key="star"
                class="star"
                :class="{filled: star <= selfRating}"
                @click="setSelfRating(star)"
            >
                ⭐
            </span>
        </div>
        
        <div class="rating-labels">
            <span>1 = Need more practice</span>
            <span>5 = Native-like</span>
        </div>
    </div>
    
    <!-- Action Buttons -->
    <div v-if="hasRecording" class="recording-actions">
        <button class="btn btn-primary" @click="saveRecording">
            💾 Save Recording
        </button>
        <button class="btn btn-secondary" @click="tryAgain">
            🔄 Try Again
        </button>
    </div>
</div>

<style>
.recording-section {
    border: 2px dashed var(--border-color);
}

.mic-permission {
    text-align: center;
    padding: var(--spacing-2xl);
}

.mic-permission p {
    margin-bottom: var(--spacing-lg);
    color: var(--text-body);
}

.recording-controls {
    display: flex;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    flex-wrap: wrap;
}

.btn-record {
    background: var(--danger);
    color: white;
    border: none;
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: var(--radius-md);
    font-weight: var(--fw-semibold);
    cursor: pointer;
    transition: var(--transition-fast);
}

.btn-record.recording {
    animation: pulse-red 1.5s infinite;
}

@keyframes pulse-red {
    0%, 100% { background: var(--danger); }
    50% { background: #ff4444; }
}

.btn-play, .btn-delete {
    background: var(--bg-light);
    border: 1px solid var(--border-color);
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: var(--transition-fast);
}

.btn-play:disabled, .btn-delete:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.recording-timer {
    display: flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--danger-light);
    color: var(--danger);
    border-radius: var(--radius-md);
    font-weight: var(--fw-semibold);
}

.recording-info {
    margin: var(--spacing-md) 0;
    color: var(--text-body);
    font-size: var(--fs-sm);
}

.self-assessment {
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-xl);
    border-top: 1px solid var(--border-light);
}

.self-assessment h4 {
    margin-bottom: var(--spacing-md);
    color: var(--primary-dark);
}

.star-rating {
    display: flex;
    gap: var(--spacing-sm);
    font-size: var(--fs-2xl);
    margin-bottom: var(--spacing-md);
}

.star {
    cursor: pointer;
    opacity: 0.3;
    transition: var(--transition-fast);
}

.star.filled {
    opacity: 1;
}

.star:hover {
    transform: scale(1.2);
}

.rating-labels {
    display: flex;
    justify-content: space-between;
    font-size: var(--fs-xs);
    color: var(--text-muted);
}

.recording-actions {
    display: flex;
    gap: var(--spacing-md);
    margin-top: var(--spacing-lg);
}
</style>
```

**4. Previous Recordings Section**
```html
<div class="previous-recordings">
    <h3>📼 Previous Recordings (Best 3)</h3>
    
    <div v-if="recordings.length === 0" class="empty-state">
        <p>No recordings yet. Start practicing!</p>
    </div>
    
    <div v-else class="recordings-grid">
        <div 
            v-for="recording in recordings" 
            :key="recording.id"
            class="recording-card"
            :class="{best: recording.is_best}"
        >
            <div class="recording-header">
                <span class="recording-date">
                    [[ formatDate(recording.created_at) ]]
                </span>
                <span v-if="recording.is_best" class="best-badge">
                    👑 Best
                </span>
            </div>
            
            <div class="recording-stars">
                <span v-for="i in 5" :key="i" class="star" :class="{filled: i <= recording.self_assessment_score}">
                    ⭐
                </span>
            </div>
            
            <div class="recording-duration">
                ⏱️ [[ recording.duration_seconds ]]s
            </div>
            
            <button class="btn-play-small" @click="playOldRecording(recording)">
                ▶️ Play
            </button>
            
            <button class="btn-delete-small" @click="deleteOldRecording(recording.id)">
                🗑️
            </button>
        </div>
    </div>
</div>

<style>
.previous-recordings {
    margin-top: var(--spacing-2xl);
}

.previous-recordings h3 {
    margin-bottom: var(--spacing-lg);
    color: var(--primary-dark);
}

.empty-state {
    text-align: center;
    padding: var(--spacing-2xl);
    color: var(--text-muted);
}

.recordings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--spacing-md);
}

.recording-card {
    background: var(--bg-white);
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    transition: var(--transition-fast);
}

.recording-card.best {
    border-color: var(--warning);
    background: var(--warning-light);
}

.recording-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.recording-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
    font-size: var(--fs-xs);
}

.recording-date {
    color: var(--text-muted);
}

.best-badge {
    background: var(--warning);
    color: white;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-weight: var(--fw-semibold);
}

.recording-stars {
    margin: var(--spacing-sm) 0;
    font-size: var(--fs-base);
}

.recording-stars .star {
    opacity: 0.3;
}

.recording-stars .star.filled {
    opacity: 1;
}

.recording-duration {
    color: var(--text-muted);
    font-size: var(--fs-sm);
    margin-bottom: var(--spacing-md);
}

.btn-play-small, .btn-delete-small {
    width: 100%;
    margin-top: var(--spacing-xs);
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    background: white;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: var(--transition-fast);
}

.btn-play-small:hover {
    background: var(--primary-orange-light);
    border-color: var(--primary-orange);
}

.btn-delete-small:hover {
    background: var(--danger-light);
    border-color: var(--danger);
}
</style>
```

---

## 📊 DAY 10: LEARNING HUB DASHBOARD UI

### Main Dashboard Page

**URL:** `/learning-hub/`

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Welcome back, [Username]! 👋               │
│  Your pronunciation progress                 │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────┬──────┬──────┬──────┐            │
│  │  44  │  20  │  78% │ 450m │            │
│  │Phon. │Mast. │Accur.│Time  │            │
│  └──────┴──────┴──────┴──────┘            │
│                                             │
│  📈 Accuracy Trend (30 Days)                │
│  ┌─────────────────────────────────────┐   │
│  │ [Line Chart]                        │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  🎯 Recommended Practice                    │
│  ┌─────────────────────────────────────┐   │
│  │ /ɪ/ - Low accuracy (65%)            │   │
│  │ [Practice Now]                      │   │
│  ├─────────────────────────────────────┤   │
│  │ /æ/ - Not practiced in 7 days       │   │
│  │ [Practice Now]                      │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  🏆 Achievements                             │
│  ┌────┬────┬────┬────┐                    │
│  │ 🎯 │ 🔥 │ 💎 │ 👑 │                    │
│  │Earn│ 7  │Lock│Lock│                    │
│  └────┴────┴────┴────┘                    │
│                                             │
│  📝 Recent Activity                         │
│  • Discrimination quiz: 8/10 (2h ago)       │
│  • Recorded /ɪ/: 4⭐ (3h ago)              │
│                                             │
└─────────────────────────────────────────────┘
```

(Component details continued in actual implementation...)

---

## 📱 RESPONSIVE DESIGN

All interfaces will be responsive:

**Desktop (1024px+):**
- 2-column grids
- Larger buttons and text
- Side-by-side comparisons

**Tablet (768px-1023px):**
- Flexible 1-2 column layouts
- Medium-sized touch targets

**Mobile (< 768px):**
- Single column
- Stack all cards vertically
- Larger touch targets (48px min)
- Bottom fixed action buttons

---

**Status:** ✅ Phase 3 UI/UX Design COMPLETE  
**Next Phase:** 4 - Implementation  
**Ready to code:** YES

Approve design? ✅/❌
