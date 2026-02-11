/* ====================================
   DICTATION ENGINE - Listening & Transcription
   Phase 3: Advanced Features
   Version: 1.0.0
   ==================================== */

/**
 * DictationEngine - Interactive dictation practice system
 * Features:
 * - Audio playback with controls
 * - Real-time transcription checking
 * - Word-by-word comparison
 * - Hints and assistance
 * - Progress tracking
 */
const DictationEngine = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        maxAttempts: 3,
        hintPenalty: 0.2,        // 20% score reduction per hint
        replayPenalty: 0.1,     // 10% reduction per extra replay
        freeReplays: 3,         // Free replays before penalty
        showWordCount: true,
        allowPartialCredit: true,
        autoPlayOnStart: true,
        playbackSpeed: 1.0,
        punctuationMatters: false,
        caseSensitive: false,
        debug: true
    },

    // State
    state: {
        currentExercise: null,
        userAnswer: '',
        attempts: 0,
        replays: 0,
        hintsUsed: 0,
        revealedWords: [],
        isPlaying: false,
        isComplete: false,
        startTime: null,
        score: 0,
        results: null
    },

    // DOM Elements
    elements: {
        container: null,
        audioPlayer: null,
        inputArea: null,
        submitBtn: null,
        hintBtn: null,
        resultArea: null
    },

    // Callbacks
    callbacks: {
        onComplete: null,
        onAttempt: null,
        onHint: null
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize dictation engine
     */
    init(container, options = {}) {
        this.config = { ...this.config, ...options };

        if (typeof container === 'string') {
            this.elements.container = document.querySelector(container);
        } else {
            this.elements.container = container;
        }

        if (!this.elements.container) {
            console.error('[DictationEngine] Container not found');
            return null;
        }

        this.log('Dictation Engine initialized');
        return this;
    },

    /**
     * Load exercise
     */
    loadExercise(exercise) {
        // Exercise format: { id, audio, transcript, title, difficulty, hints }
        this.state.currentExercise = exercise;
        this.resetState();
        this.renderUI();
        
        if (this.config.autoPlayOnStart) {
            setTimeout(() => this.playAudio(), 500);
        }

        this.log('Exercise loaded:', exercise.title);
        return this;
    },

    /**
     * Reset state
     */
    resetState() {
        this.state.userAnswer = '';
        this.state.attempts = 0;
        this.state.replays = 0;
        this.state.hintsUsed = 0;
        this.state.revealedWords = [];
        this.state.isPlaying = false;
        this.state.isComplete = false;
        this.state.startTime = Date.now();
        this.state.score = 0;
        this.state.results = null;
    },

    // ====================================
    // UI RENDERING
    // ====================================
    
    /**
     * Render dictation UI
     */
    renderUI() {
        const exercise = this.state.currentExercise;
        const wordCount = this.getWordCount(exercise.transcript);

        const html = `
            <div class="dictation-container">
                <!-- Header -->
                <div class="dictation-header">
                    <div class="exercise-info">
                        <h3 class="exercise-title">${exercise.title || 'Dictation Exercise'}</h3>
                        <div class="exercise-meta">
                            <span class="difficulty-badge difficulty-${exercise.difficulty || 'medium'}">
                                ${this.getDifficultyLabel(exercise.difficulty)}
                            </span>
                            ${this.config.showWordCount ? `<span class="word-count">${wordCount} từ</span>` : ''}
                        </div>
                    </div>
                    <div class="attempt-info">
                        <span>Lần thử: <strong>${this.state.attempts}/${this.config.maxAttempts}</strong></span>
                    </div>
                </div>

                <!-- Audio Player -->
                <div class="dictation-player">
                    <div class="player-controls">
                        <button class="btn-player btn-replay" title="Phát lại">
                            <i class="fas fa-redo"></i>
                        </button>
                        <button class="btn-player btn-play-main" title="Phát/Dừng">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn-player btn-slow" title="Phát chậm (0.75x)">
                            <i class="fas fa-turtle"></i>
                        </button>
                    </div>
                    <div class="player-progress">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <span class="replay-count">Đã nghe: ${this.state.replays} lần</span>
                    </div>
                    <audio class="audio-element" src="${exercise.audio}" preload="auto"></audio>
                </div>

                <!-- Input Area -->
                <div class="dictation-input">
                    <textarea 
                        class="dictation-textarea" 
                        placeholder="Nghe và gõ lại những gì bạn nghe được..."
                        rows="4"
                    >${this.state.userAnswer}</textarea>
                    
                    <!-- Hint Area -->
                    <div class="hint-area" style="display: none;">
                        <div class="hint-words"></div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="dictation-actions">
                    <button class="btn-hint" ${this.state.hintsUsed >= 3 ? 'disabled' : ''}>
                        <i class="fas fa-lightbulb"></i>
                        Gợi ý (${3 - this.state.hintsUsed} còn lại)
                    </button>
                    <button class="btn-submit">
                        <i class="fas fa-check"></i>
                        Kiểm tra
                    </button>
                </div>

                <!-- Results Area (hidden initially) -->
                <div class="dictation-results" style="display: none;"></div>
            </div>
        `;

        this.elements.container.innerHTML = html;
        this.cacheElements();
        this.bindEvents();
        this.injectStyles();
    },

    /**
     * Cache DOM elements
     */
    cacheElements() {
        const c = this.elements.container;
        this.elements.audioPlayer = c.querySelector('.audio-element');
        this.elements.inputArea = c.querySelector('.dictation-textarea');
        this.elements.submitBtn = c.querySelector('.btn-submit');
        this.elements.hintBtn = c.querySelector('.btn-hint');
        this.elements.resultArea = c.querySelector('.dictation-results');
        this.elements.playBtn = c.querySelector('.btn-play-main');
        this.elements.replayBtn = c.querySelector('.btn-replay');
        this.elements.slowBtn = c.querySelector('.btn-slow');
        this.elements.progressFill = c.querySelector('.progress-fill');
        this.elements.replayCount = c.querySelector('.replay-count');
        this.elements.hintArea = c.querySelector('.hint-area');
        this.elements.attemptInfo = c.querySelector('.attempt-info strong');
    },

    /**
     * Bind events
     */
    bindEvents() {
        const audio = this.elements.audioPlayer;

        // Audio events
        audio.addEventListener('play', () => this.onAudioPlay());
        audio.addEventListener('pause', () => this.onAudioPause());
        audio.addEventListener('ended', () => this.onAudioEnded());
        audio.addEventListener('timeupdate', () => this.onTimeUpdate());

        // Control buttons
        this.elements.playBtn.addEventListener('click', () => this.togglePlay());
        this.elements.replayBtn.addEventListener('click', () => this.replay());
        this.elements.slowBtn.addEventListener('click', () => this.playSlow());

        // Submit and hint
        this.elements.submitBtn.addEventListener('click', () => this.checkAnswer());
        this.elements.hintBtn.addEventListener('click', () => this.showHint());

        // Input tracking
        this.elements.inputArea.addEventListener('input', (e) => {
            this.state.userAnswer = e.target.value;
        });

        // Keyboard shortcuts
        this.elements.inputArea.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.checkAnswer();
            }
            if (e.ctrlKey && e.key === ' ') {
                e.preventDefault();
                this.togglePlay();
            }
        });
    },

    /**
     * Inject styles
     */
    injectStyles() {
        if (document.getElementById('dictationStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'dictationStyles';
        styles.textContent = `
            .dictation-container {
                background: white;
                border-radius: 16px;
                padding: 32px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            }
            
            .dictation-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 24px;
            }
            
            .exercise-title {
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
                font-size: 1.25rem;
                color: #183B56;
                margin: 0 0 8px 0;
            }
            
            .exercise-meta {
                display: flex;
                gap: 12px;
                align-items: center;
            }
            
            .difficulty-badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            
            .difficulty-easy { background: #E8F5E9; color: #27AE60; }
            .difficulty-medium { background: #FFF3E0; color: #F47C26; }
            .difficulty-hard { background: #FFEBEE; color: #E74C3C; }
            
            .word-count {
                color: #6c757d;
                font-size: 0.875rem;
            }
            
            .attempt-info {
                color: #6c757d;
                font-size: 0.9rem;
            }
            
            .dictation-player {
                background: #F9FAFC;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 24px;
            }
            
            .player-controls {
                display: flex;
                justify-content: center;
                gap: 16px;
                margin-bottom: 16px;
            }
            
            .btn-player {
                width: 50px;
                height: 50px;
                border: none;
                border-radius: 50%;
                background: white;
                color: #183B56;
                font-size: 1.25rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            
            .btn-player:hover {
                background: #F47C26;
                color: white;
                transform: scale(1.05);
            }
            
            .btn-play-main {
                width: 60px;
                height: 60px;
                background: #F47C26;
                color: white;
            }
            
            .btn-play-main:hover {
                background: #D35400;
            }
            
            .btn-play-main.playing {
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(244, 124, 38, 0.5); }
                70% { box-shadow: 0 0 0 15px rgba(244, 124, 38, 0); }
                100% { box-shadow: 0 0 0 0 rgba(244, 124, 38, 0); }
            }
            
            .player-progress {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .progress-bar {
                flex: 1;
                height: 6px;
                background: #E0E6ED;
                border-radius: 3px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: #F47C26;
                width: 0%;
                transition: width 0.1s linear;
            }
            
            .replay-count {
                font-size: 0.85rem;
                color: #6c757d;
                white-space: nowrap;
            }
            
            .dictation-input {
                margin-bottom: 20px;
            }
            
            .dictation-textarea {
                width: 100%;
                padding: 16px;
                border: 2px solid #E0E6ED;
                border-radius: 12px;
                font-size: 1rem;
                line-height: 1.6;
                resize: vertical;
                transition: border-color 0.3s ease;
                font-family: 'Open Sans', sans-serif;
            }
            
            .dictation-textarea:focus {
                outline: none;
                border-color: #F47C26;
            }
            
            .dictation-textarea.correct {
                border-color: #27AE60;
                background: #E8F5E9;
            }
            
            .dictation-textarea.incorrect {
                border-color: #E74C3C;
                background: #FFEBEE;
            }
            
            .hint-area {
                margin-top: 12px;
                padding: 16px;
                background: #FFF9E6;
                border-radius: 8px;
                border-left: 4px solid #FFC107;
            }
            
            .hint-words {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            
            .hint-word {
                padding: 4px 12px;
                background: white;
                border-radius: 4px;
                font-size: 0.9rem;
                color: #183B56;
            }
            
            .hint-word.revealed {
                background: #F47C26;
                color: white;
            }
            
            .dictation-actions {
                display: flex;
                gap: 16px;
                justify-content: center;
            }
            
            .btn-hint, .btn-submit {
                padding: 12px 32px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .btn-hint {
                background: #FFF3E0;
                color: #F47C26;
            }
            
            .btn-hint:hover:not(:disabled) {
                background: #FFE0B2;
            }
            
            .btn-hint:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .btn-submit {
                background: #F47C26;
                color: white;
            }
            
            .btn-submit:hover {
                background: #D35400;
            }
            
            .dictation-results {
                margin-top: 24px;
                padding: 24px;
                border-radius: 12px;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .score-display {
                text-align: center;
            }
            
            .score-value {
                font-family: 'Montserrat', sans-serif;
                font-size: 3rem;
                font-weight: 800;
                color: #183B56;
            }
            
            .score-label {
                font-size: 0.9rem;
                color: #6c757d;
            }
            
            .comparison-text {
                line-height: 2;
                font-size: 1.1rem;
            }
            
            .word-correct {
                color: #27AE60;
                background: #E8F5E9;
                padding: 2px 6px;
                border-radius: 4px;
            }
            
            .word-incorrect {
                color: #E74C3C;
                background: #FFEBEE;
                padding: 2px 6px;
                border-radius: 4px;
                text-decoration: line-through;
            }
            
            .word-missing {
                color: #3498DB;
                background: #E3F2FD;
                padding: 2px 6px;
                border-radius: 4px;
            }
            
            .word-extra {
                color: #9B59B6;
                background: #F3E5F5;
                padding: 2px 6px;
                border-radius: 4px;
            }
            
            .results-stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-top: 20px;
            }
            
            .stat-item {
                text-align: center;
                padding: 12px;
                background: #F9FAFC;
                border-radius: 8px;
            }
            
            .stat-item-value {
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
                font-size: 1.5rem;
                color: #183B56;
            }
            
            .stat-item-label {
                font-size: 0.8rem;
                color: #6c757d;
            }
            
            .results-actions {
                display: flex;
                gap: 12px;
                justify-content: center;
                margin-top: 24px;
            }
            
            .btn-retry, .btn-next {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-retry {
                background: #E0E6ED;
                color: #183B56;
            }
            
            .btn-next {
                background: #27AE60;
                color: white;
            }
            
            /* Mobile responsive */
            @media (max-width: 576px) {
                .dictation-container {
                    padding: 20px;
                }
                
                .dictation-header {
                    flex-direction: column;
                    gap: 12px;
                }
                
                .player-controls {
                    gap: 12px;
                }
                
                .btn-player {
                    width: 44px;
                    height: 44px;
                }
                
                .btn-play-main {
                    width: 54px;
                    height: 54px;
                }
                
                .dictation-actions {
                    flex-direction: column;
                }
                
                .results-stats {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        `;

        document.head.appendChild(styles);
    },

    // ====================================
    // AUDIO CONTROL
    // ====================================
    
    playAudio() {
        this.elements.audioPlayer.playbackRate = this.config.playbackSpeed;
        this.elements.audioPlayer.play();
    },

    pauseAudio() {
        this.elements.audioPlayer.pause();
    },

    togglePlay() {
        if (this.state.isPlaying) {
            this.pauseAudio();
        } else {
            this.playAudio();
        }
    },

    replay() {
        this.elements.audioPlayer.currentTime = 0;
        this.state.replays++;
        this.updateReplayCount();
        this.playAudio();
    },

    playSlow() {
        this.elements.audioPlayer.playbackRate = 0.75;
        this.elements.audioPlayer.currentTime = 0;
        this.state.replays++;
        this.updateReplayCount();
        this.playAudio();
    },

    onAudioPlay() {
        this.state.isPlaying = true;
        this.elements.playBtn.classList.add('playing');
        this.elements.playBtn.querySelector('i').className = 'fas fa-pause';
    },

    onAudioPause() {
        this.state.isPlaying = false;
        this.elements.playBtn.classList.remove('playing');
        this.elements.playBtn.querySelector('i').className = 'fas fa-play';
    },

    onAudioEnded() {
        this.state.isPlaying = false;
        this.elements.playBtn.classList.remove('playing');
        this.elements.playBtn.querySelector('i').className = 'fas fa-play';
        this.elements.audioPlayer.playbackRate = this.config.playbackSpeed;
    },

    onTimeUpdate() {
        const audio = this.elements.audioPlayer;
        const percent = (audio.currentTime / audio.duration) * 100;
        this.elements.progressFill.style.width = percent + '%';
    },

    updateReplayCount() {
        this.elements.replayCount.textContent = `Đã nghe: ${this.state.replays} lần`;
    },

    // ====================================
    // HINT SYSTEM
    // ====================================
    
    showHint() {
        if (this.state.hintsUsed >= 3) return;

        const transcript = this.state.currentExercise.transcript;
        const words = this.normalizeText(transcript).split(/\s+/);
        
        // Find a word that hasn't been revealed yet
        const unrevealedIndices = words
            .map((_, i) => i)
            .filter(i => !this.state.revealedWords.includes(i));

        if (unrevealedIndices.length === 0) return;

        // Reveal a random word
        const randomIndex = unrevealedIndices[Math.floor(Math.random() * unrevealedIndices.length)];
        this.state.revealedWords.push(randomIndex);
        this.state.hintsUsed++;

        // Update hint display
        this.renderHints(words);
        
        // Update hint button
        this.elements.hintBtn.innerHTML = `
            <i class="fas fa-lightbulb"></i>
            Gợi ý (${3 - this.state.hintsUsed} còn lại)
        `;
        
        if (this.state.hintsUsed >= 3) {
            this.elements.hintBtn.disabled = true;
        }

        if (this.callbacks.onHint) {
            this.callbacks.onHint(this.state.hintsUsed);
        }
    },

    renderHints(words) {
        this.elements.hintArea.style.display = 'block';
        
        const hintsHtml = words.map((word, i) => {
            if (this.state.revealedWords.includes(i)) {
                return `<span class="hint-word revealed">${word}</span>`;
            }
            return `<span class="hint-word">____</span>`;
        }).join('');

        this.elements.hintArea.querySelector('.hint-words').innerHTML = hintsHtml;
    },

    // ====================================
    // ANSWER CHECKING
    // ====================================
    
    checkAnswer() {
        if (this.state.isComplete) return;

        this.state.attempts++;
        this.updateAttemptDisplay();

        const userAnswer = this.state.userAnswer.trim();
        const correctAnswer = this.state.currentExercise.transcript;

        // Compare answers
        const result = this.compareTexts(userAnswer, correctAnswer);
        
        // Calculate score with penalties
        let score = result.accuracy;
        
        // Apply hint penalty
        score -= this.state.hintsUsed * this.config.hintPenalty * 100;
        
        // Apply replay penalty (after free replays)
        const extraReplays = Math.max(0, this.state.replays - this.config.freeReplays);
        score -= extraReplays * this.config.replayPenalty * 100;
        
        // Ensure score is between 0-100
        score = Math.max(0, Math.min(100, Math.round(score)));

        this.state.score = score;
        this.state.results = result;

        // Check if complete (correct answer or max attempts)
        if (result.accuracy >= 95 || this.state.attempts >= this.config.maxAttempts) {
            this.state.isComplete = true;
            this.showResults(result, score);
        } else {
            // Show partial feedback
            this.showPartialFeedback(result);
        }

        if (this.callbacks.onAttempt) {
            this.callbacks.onAttempt(this.state.attempts, result);
        }
    },

    /**
     * Compare user text with correct text
     */
    compareTexts(userText, correctText) {
        const normalize = (text) => {
            let normalized = text.toLowerCase();
            if (!this.config.punctuationMatters) {
                normalized = normalized.replace(/[^\w\s]/g, '');
            }
            return normalized.replace(/\s+/g, ' ').trim();
        };

        const userWords = normalize(userText).split(' ');
        const correctWords = normalize(correctText).split(' ');

        const result = {
            userWords: [],
            correctWords: correctWords,
            correctCount: 0,
            incorrectCount: 0,
            missingCount: 0,
            extraCount: 0,
            accuracy: 0
        };

        // Use Longest Common Subsequence for comparison
        const comparison = this.compareWordArrays(userWords, correctWords);
        
        result.userWords = comparison.userComparison;
        result.correctCount = comparison.matches;
        result.incorrectCount = comparison.incorrect;
        result.missingCount = comparison.missing;
        result.extraCount = comparison.extra;
        result.accuracy = correctWords.length > 0 
            ? (comparison.matches / correctWords.length) * 100 
            : 0;

        return result;
    },

    /**
     * Compare two word arrays
     */
    compareWordArrays(userWords, correctWords) {
        const userComparison = [];
        let matches = 0;
        let incorrect = 0;
        let missing = 0;
        let extra = 0;

        // Simple word-by-word comparison
        const maxLen = Math.max(userWords.length, correctWords.length);
        
        for (let i = 0; i < maxLen; i++) {
            const userWord = userWords[i] || '';
            const correctWord = correctWords[i] || '';

            if (!userWord && correctWord) {
                // Missing word
                userComparison.push({ word: correctWord, status: 'missing' });
                missing++;
            } else if (userWord && !correctWord) {
                // Extra word
                userComparison.push({ word: userWord, status: 'extra' });
                extra++;
            } else if (userWord === correctWord) {
                // Correct
                userComparison.push({ word: userWord, status: 'correct' });
                matches++;
            } else {
                // Incorrect
                userComparison.push({ word: userWord, status: 'incorrect', expected: correctWord });
                incorrect++;
            }
        }

        return { userComparison, matches, incorrect, missing, extra };
    },

    /**
     * Show partial feedback after failed attempt
     */
    showPartialFeedback(result) {
        const textarea = this.elements.inputArea;
        textarea.classList.add('incorrect');
        
        setTimeout(() => {
            textarea.classList.remove('incorrect');
        }, 1000);

        // Show toast if available
        if (typeof UIComponents !== 'undefined') {
            const remaining = this.config.maxAttempts - this.state.attempts;
            UIComponents.toast.warning(`Chưa chính xác. Còn ${remaining} lần thử.`);
        }
    },

    /**
     * Show final results
     */
    showResults(result, score) {
        const timeSpent = Math.round((Date.now() - this.state.startTime) / 1000);

        const resultHtml = `
            <div class="results-header">
                <div class="score-display">
                    <div class="score-value ${this.getScoreClass(score)}">${score}%</div>
                    <div class="score-label">${this.getScoreLabel(score)}</div>
                </div>
            </div>
            
            <h4 style="margin-bottom: 16px;">So sánh kết quả:</h4>
            <div class="comparison-text">
                ${this.renderComparison(result)}
            </div>
            
            <h4 style="margin: 24px 0 16px;">Đáp án đúng:</h4>
            <div class="correct-answer" style="padding: 16px; background: #E8F5E9; border-radius: 8px; line-height: 1.8;">
                ${this.state.currentExercise.transcript}
            </div>
            
            <div class="results-stats">
                <div class="stat-item">
                    <div class="stat-item-value">${result.correctCount}</div>
                    <div class="stat-item-label">Từ đúng</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-value">${result.incorrectCount + result.missingCount}</div>
                    <div class="stat-item-label">Từ sai/thiếu</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-value">${this.state.replays}</div>
                    <div class="stat-item-label">Lần nghe</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-value">${this.formatTime(timeSpent)}</div>
                    <div class="stat-item-label">Thời gian</div>
                </div>
            </div>
            
            <div class="results-actions">
                <button class="btn-retry" onclick="DictationEngine.retry()">
                    <i class="fas fa-redo"></i> Làm lại
                </button>
                <button class="btn-next" onclick="DictationEngine.complete()">
                    Tiếp tục <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        `;

        this.elements.resultArea.innerHTML = resultHtml;
        this.elements.resultArea.style.display = 'block';
        this.elements.resultArea.style.background = score >= 80 ? '#E8F5E9' : score >= 50 ? '#FFF3E0' : '#FFEBEE';

        // Disable input
        this.elements.inputArea.disabled = true;
        this.elements.submitBtn.disabled = true;
        this.elements.hintBtn.disabled = true;

        // Log to progress tracker if available
        if (typeof ProgressTracker !== 'undefined') {
            ProgressTracker.logExercise('listening', score, timeSpent / 60);
        }
    },

    /**
     * Render comparison HTML
     */
    renderComparison(result) {
        return result.userWords.map(item => {
            switch (item.status) {
                case 'correct':
                    return `<span class="word-correct">${item.word}</span>`;
                case 'incorrect':
                    return `<span class="word-incorrect">${item.word}</span><span class="word-missing">${item.expected}</span>`;
                case 'missing':
                    return `<span class="word-missing">[${item.word}]</span>`;
                case 'extra':
                    return `<span class="word-extra">${item.word}</span>`;
                default:
                    return item.word;
            }
        }).join(' ');
    },

    // ====================================
    // NAVIGATION
    // ====================================
    
    retry() {
        this.loadExercise(this.state.currentExercise);
    },

    complete() {
        if (this.callbacks.onComplete) {
            this.callbacks.onComplete({
                score: this.state.score,
                attempts: this.state.attempts,
                replays: this.state.replays,
                hintsUsed: this.state.hintsUsed,
                timeSpent: Date.now() - this.state.startTime,
                results: this.state.results
            });
        }
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    normalizeText(text) {
        let normalized = text;
        if (!this.config.caseSensitive) {
            normalized = normalized.toLowerCase();
        }
        if (!this.config.punctuationMatters) {
            normalized = normalized.replace(/[^\w\s]/g, '');
        }
        return normalized.replace(/\s+/g, ' ').trim();
    },

    getWordCount(text) {
        return text.trim().split(/\s+/).length;
    },

    getDifficultyLabel(difficulty) {
        const labels = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' };
        return labels[difficulty] || 'Trung bình';
    },

    getScoreClass(score) {
        if (score >= 80) return 'text-success';
        if (score >= 50) return 'text-warning';
        return 'text-danger';
    },

    getScoreLabel(score) {
        if (score >= 90) return 'Xuất sắc!';
        if (score >= 80) return 'Tốt lắm!';
        if (score >= 60) return 'Khá tốt';
        if (score >= 40) return 'Cần cố gắng';
        return 'Cần luyện tập thêm';
    },

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    updateAttemptDisplay() {
        this.elements.attemptInfo.textContent = `${this.state.attempts}/${this.config.maxAttempts}`;
    },

    on(event, callback) {
        const eventName = 'on' + event.charAt(0).toUpperCase() + event.slice(1);
        if (this.callbacks.hasOwnProperty(eventName)) {
            this.callbacks[eventName] = callback;
        }
        return this;
    },

    log(...args) {
        if (this.config.debug) {
            console.log('[DictationEngine]', ...args);
        }
    }
};

// Export
window.DictationEngine = DictationEngine;

console.log('[Dictation Engine] Module loaded');
