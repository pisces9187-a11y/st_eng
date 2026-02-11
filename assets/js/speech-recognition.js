/* ====================================
   SPEECH RECOGNITION - Web Speech API
   Phase 2: Core Features
   Version: 1.0.0
   ==================================== */

/**
 * SpeechRecognition - Voice input and pronunciation assessment
 * Features:
 * - Speech-to-text conversion
 * - Pronunciation comparison
 * - Real-time feedback
 * - Multiple language support
 */
const SpeechRecognizer = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        lang: 'en-US',
        continuous: false,
        interimResults: true,
        maxAlternatives: 3,
        autoStop: true,
        autoStopTimeout: 3000,
        minConfidence: 0.7,
        debug: true
    },

    // State
    state: {
        isSupported: false,
        isListening: false,
        recognition: null,
        transcript: '',
        interimTranscript: '',
        confidence: 0,
        alternatives: [],
        error: null,
        autoStopTimer: null
    },

    // Callbacks
    callbacks: {
        onStart: null,
        onEnd: null,
        onResult: null,
        onInterim: null,
        onError: null,
        onNoMatch: null
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize speech recognition
     */
    init(options = {}) {
        this.config = { ...this.config, ...options };

        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            this.state.isSupported = false;
            this.log('Speech Recognition not supported');
            return this;
        }

        this.state.isSupported = true;
        this.state.recognition = new SpeechRecognition();
        
        // Configure
        this.state.recognition.lang = this.config.lang;
        this.state.recognition.continuous = this.config.continuous;
        this.state.recognition.interimResults = this.config.interimResults;
        this.state.recognition.maxAlternatives = this.config.maxAlternatives;

        // Bind events
        this.bindEvents();

        this.log('Speech Recognition initialized');
        return this;
    },

    /**
     * Bind recognition events
     */
    bindEvents() {
        const recognition = this.state.recognition;

        recognition.onstart = () => {
            this.state.isListening = true;
            this.state.transcript = '';
            this.state.interimTranscript = '';
            this.state.error = null;

            this.log('Recognition started');

            if (this.callbacks.onStart) {
                this.callbacks.onStart();
            }

            // Start auto-stop timer
            if (this.config.autoStop) {
                this.startAutoStopTimer();
            }
        };

        recognition.onend = () => {
            this.state.isListening = false;
            this.clearAutoStopTimer();

            this.log('Recognition ended');

            if (this.callbacks.onEnd) {
                this.callbacks.onEnd(this.state.transcript, this.state.confidence);
            }
        };

        recognition.onresult = (event) => {
            this.handleResult(event);
        };

        recognition.onerror = (event) => {
            this.state.error = event.error;
            this.log('Recognition error:', event.error);

            if (this.callbacks.onError) {
                this.callbacks.onError(event.error, event.message);
            }
        };

        recognition.onnomatch = () => {
            this.log('No match found');

            if (this.callbacks.onNoMatch) {
                this.callbacks.onNoMatch();
            }
        };
    },

    /**
     * Handle recognition result
     */
    handleResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            const transcript = result[0].transcript;

            if (result.isFinal) {
                finalTranscript += transcript;
                this.state.confidence = result[0].confidence;
                
                // Get alternatives
                this.state.alternatives = [];
                for (let j = 0; j < result.length && j < this.config.maxAlternatives; j++) {
                    this.state.alternatives.push({
                        transcript: result[j].transcript,
                        confidence: result[j].confidence
                    });
                }
            } else {
                interimTranscript += transcript;
            }
        }

        if (finalTranscript) {
            this.state.transcript = finalTranscript.trim();
            this.resetAutoStopTimer();

            this.log('Final result:', this.state.transcript, 'Confidence:', this.state.confidence);

            if (this.callbacks.onResult) {
                this.callbacks.onResult(this.state.transcript, this.state.confidence, this.state.alternatives);
            }
        }

        if (interimTranscript) {
            this.state.interimTranscript = interimTranscript;
            this.resetAutoStopTimer();

            if (this.callbacks.onInterim) {
                this.callbacks.onInterim(interimTranscript);
            }
        }
    },

    // ====================================
    // CONTROL METHODS
    // ====================================
    
    /**
     * Start listening
     */
    start() {
        if (!this.state.isSupported) {
            this.log('Speech Recognition not supported');
            return false;
        }

        if (this.state.isListening) {
            this.log('Already listening');
            return false;
        }

        try {
            this.state.recognition.start();
            return true;
        } catch (error) {
            this.log('Start error:', error);
            return false;
        }
    },

    /**
     * Stop listening
     */
    stop() {
        if (!this.state.isListening) return;

        try {
            this.state.recognition.stop();
            this.clearAutoStopTimer();
        } catch (error) {
            this.log('Stop error:', error);
        }
    },

    /**
     * Abort recognition
     */
    abort() {
        if (!this.state.isListening) return;

        try {
            this.state.recognition.abort();
            this.clearAutoStopTimer();
        } catch (error) {
            this.log('Abort error:', error);
        }
    },

    /**
     * Toggle listening
     */
    toggle() {
        if (this.state.isListening) {
            this.stop();
        } else {
            this.start();
        }
    },

    // ====================================
    // AUTO STOP TIMER
    // ====================================
    
    startAutoStopTimer() {
        this.clearAutoStopTimer();
        this.state.autoStopTimer = setTimeout(() => {
            if (this.state.isListening) {
                this.log('Auto-stopping due to silence');
                this.stop();
            }
        }, this.config.autoStopTimeout);
    },

    resetAutoStopTimer() {
        if (this.config.autoStop && this.state.isListening) {
            this.startAutoStopTimer();
        }
    },

    clearAutoStopTimer() {
        if (this.state.autoStopTimer) {
            clearTimeout(this.state.autoStopTimer);
            this.state.autoStopTimer = null;
        }
    },

    // ====================================
    // LANGUAGE
    // ====================================
    
    /**
     * Set recognition language
     */
    setLanguage(lang) {
        this.config.lang = lang;
        if (this.state.recognition) {
            this.state.recognition.lang = lang;
        }
        this.log('Language set to:', lang);
    },

    /**
     * Get supported languages
     */
    getSupportedLanguages() {
        return [
            { code: 'en-US', name: 'English (US)' },
            { code: 'en-GB', name: 'English (UK)' },
            { code: 'en-AU', name: 'English (Australia)' },
            { code: 'vi-VN', name: 'Tiếng Việt' },
            { code: 'ja-JP', name: '日本語' },
            { code: 'ko-KR', name: '한국어' },
            { code: 'zh-CN', name: '中文 (简体)' },
            { code: 'fr-FR', name: 'Français' },
            { code: 'de-DE', name: 'Deutsch' },
            { code: 'es-ES', name: 'Español' }
        ];
    },

    // ====================================
    // PRONUNCIATION ASSESSMENT
    // ====================================
    
    /**
     * Compare spoken text with expected text
     * @param {string} expected - Expected text
     * @param {string} spoken - Spoken text (or use current transcript)
     * @returns {Object} Comparison result
     */
    comparePronunciation(expected, spoken = null) {
        spoken = spoken || this.state.transcript;
        
        if (!expected || !spoken) {
            return { score: 0, matches: [], mismatches: [], accuracy: 0 };
        }

        // Normalize texts
        const normalizedExpected = this.normalizeText(expected);
        const normalizedSpoken = this.normalizeText(spoken);

        // Split into words
        const expectedWords = normalizedExpected.split(/\s+/);
        const spokenWords = normalizedSpoken.split(/\s+/);

        // Calculate word-level accuracy
        const matches = [];
        const mismatches = [];
        let matchCount = 0;

        // Use longest common subsequence approach
        for (let i = 0; i < expectedWords.length; i++) {
            const expectedWord = expectedWords[i];
            const spokenWord = spokenWords[i] || '';
            
            const similarity = this.calculateSimilarity(expectedWord, spokenWord);
            
            if (similarity >= 0.8) {
                matches.push({ word: expectedWord, spoken: spokenWord, similarity, index: i });
                matchCount++;
            } else {
                mismatches.push({ word: expectedWord, spoken: spokenWord, similarity, index: i });
            }
        }

        // Calculate overall score
        const accuracy = expectedWords.length > 0 
            ? Math.round((matchCount / expectedWords.length) * 100) 
            : 0;

        // Combine with recognition confidence
        const confidenceWeight = 0.3;
        const accuracyWeight = 0.7;
        const score = Math.round(
            (this.state.confidence * 100 * confidenceWeight) + 
            (accuracy * accuracyWeight)
        );

        return {
            score,
            accuracy,
            confidence: Math.round(this.state.confidence * 100),
            matches,
            mismatches,
            expected: normalizedExpected,
            spoken: normalizedSpoken,
            feedback: this.generateFeedback(score, mismatches)
        };
    },

    /**
     * Normalize text for comparison
     */
    normalizeText(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s]/g, '') // Remove punctuation
            .replace(/\s+/g, ' ')     // Normalize whitespace
            .trim();
    },

    /**
     * Calculate similarity between two strings (Levenshtein-based)
     */
    calculateSimilarity(str1, str2) {
        if (!str1 || !str2) return 0;
        if (str1 === str2) return 1;

        const len1 = str1.length;
        const len2 = str2.length;
        const matrix = [];

        // Build matrix
        for (let i = 0; i <= len1; i++) {
            matrix[i] = [i];
        }
        for (let j = 0; j <= len2; j++) {
            matrix[0][j] = j;
        }

        // Fill matrix
        for (let i = 1; i <= len1; i++) {
            for (let j = 1; j <= len2; j++) {
                const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
                matrix[i][j] = Math.min(
                    matrix[i - 1][j] + 1,      // Deletion
                    matrix[i][j - 1] + 1,      // Insertion
                    matrix[i - 1][j - 1] + cost // Substitution
                );
            }
        }

        const distance = matrix[len1][len2];
        const maxLen = Math.max(len1, len2);
        return maxLen > 0 ? (maxLen - distance) / maxLen : 1;
    },

    /**
     * Generate pronunciation feedback
     */
    generateFeedback(score, mismatches) {
        const feedback = {
            level: '',
            message: '',
            suggestions: []
        };

        if (score >= 90) {
            feedback.level = 'excellent';
            feedback.message = 'Xuất sắc! Phát âm của bạn rất chuẩn.';
        } else if (score >= 75) {
            feedback.level = 'good';
            feedback.message = 'Tốt lắm! Phát âm khá chính xác.';
        } else if (score >= 50) {
            feedback.level = 'fair';
            feedback.message = 'Khá được. Cần luyện tập thêm một số từ.';
        } else {
            feedback.level = 'needs-work';
            feedback.message = 'Cần cải thiện. Hãy nghe lại và thử lại.';
        }

        // Add specific word suggestions
        if (mismatches.length > 0) {
            feedback.suggestions = mismatches.slice(0, 3).map(m => ({
                word: m.word,
                spoken: m.spoken || '(không nghe rõ)',
                tip: `Từ "${m.word}" cần phát âm rõ hơn.`
            }));
        }

        return feedback;
    },

    // ====================================
    // PRACTICE MODE
    // ====================================
    
    /**
     * Practice pronunciation of a sentence
     * @param {string} sentence - Sentence to practice
     * @returns {Promise} Resolves with comparison result
     */
    practice(sentence) {
        return new Promise((resolve, reject) => {
            if (!this.state.isSupported) {
                reject(new Error('Speech Recognition not supported'));
                return;
            }

            const originalCallback = this.callbacks.onEnd;
            
            this.callbacks.onEnd = (transcript, confidence) => {
                const result = this.comparePronunciation(sentence);
                this.callbacks.onEnd = originalCallback;
                resolve(result);
            };

            const originalErrorCallback = this.callbacks.onError;
            
            this.callbacks.onError = (error, message) => {
                this.callbacks.onError = originalErrorCallback;
                reject(new Error(error));
            };

            this.start();
        });
    },

    /**
     * Repeat after audio (listen and speak)
     */
    async repeatAfter(text, audioUrl = null) {
        // Play audio first
        if (audioUrl) {
            const audio = new Audio(audioUrl);
            await new Promise(resolve => {
                audio.onended = resolve;
                audio.play();
            });
        } else {
            // Use TTS
            await this.speakText(text);
        }

        // Wait a bit, then start listening
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return this.practice(text);
    },

    /**
     * Speak text using TTS
     */
    speakText(text, lang = 'en-US') {
        return new Promise((resolve, reject) => {
            if (!('speechSynthesis' in window)) {
                reject(new Error('TTS not supported'));
                return;
            }

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            utterance.rate = 0.9;
            utterance.onend = resolve;
            utterance.onerror = reject;

            speechSynthesis.speak(utterance);
        });
    },

    // ====================================
    // EVENT CALLBACKS
    // ====================================
    
    /**
     * Set event callback
     */
    on(event, callback) {
        const eventName = 'on' + event.charAt(0).toUpperCase() + event.slice(1);
        if (this.callbacks.hasOwnProperty(eventName)) {
            this.callbacks[eventName] = callback;
        }
        return this;
    },

    /**
     * Remove event callback
     */
    off(event) {
        const eventName = 'on' + event.charAt(0).toUpperCase() + event.slice(1);
        if (this.callbacks.hasOwnProperty(eventName)) {
            this.callbacks[eventName] = null;
        }
        return this;
    },

    // ====================================
    // UI HELPERS
    // ====================================
    
    /**
     * Create microphone button UI
     */
    createMicButton(container, options = {}) {
        const { 
            size = 'normal', 
            showWave = true,
            onResult = null 
        } = options;

        const sizeClass = size === 'large' ? 'mic-btn-large' : '';
        
        const html = `
            <div class="speech-mic-container ${sizeClass}">
                <button class="speech-mic-btn" type="button">
                    <i class="fas fa-microphone"></i>
                </button>
                ${showWave ? '<div class="speech-wave"></div>' : ''}
                <div class="speech-status"></div>
            </div>
        `;

        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        container.innerHTML = html;

        const btn = container.querySelector('.speech-mic-btn');
        const status = container.querySelector('.speech-status');
        const wave = container.querySelector('.speech-wave');

        // Handle click
        btn.addEventListener('click', () => {
            this.toggle();
        });

        // Update UI on events
        this.on('start', () => {
            btn.classList.add('listening');
            if (wave) wave.classList.add('active');
            status.textContent = 'Đang nghe...';
        });

        this.on('end', (transcript) => {
            btn.classList.remove('listening');
            if (wave) wave.classList.remove('active');
            status.textContent = transcript ? 'Đã ghi nhận' : '';
            
            if (onResult && transcript) {
                onResult(transcript, this.state.confidence);
            }
        });

        this.on('interim', (text) => {
            status.textContent = text;
        });

        this.on('error', (error) => {
            btn.classList.remove('listening');
            if (wave) wave.classList.remove('active');
            status.textContent = this.getErrorMessage(error);
        });

        // Inject styles
        this.injectMicStyles();

        return btn;
    },

    /**
     * Inject microphone button styles
     */
    injectMicStyles() {
        if (document.getElementById('speechMicStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'speechMicStyles';
        styles.textContent = `
            .speech-mic-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 12px;
            }
            
            .speech-mic-btn {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                border: none;
                background: #F47C26;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                z-index: 1;
            }
            
            .speech-mic-btn:hover {
                background: #D35400;
                transform: scale(1.05);
            }
            
            .speech-mic-btn.listening {
                background: #dc3545;
                animation: pulse 1.5s infinite;
            }
            
            .speech-mic-container.mic-btn-large .speech-mic-btn {
                width: 80px;
                height: 80px;
                font-size: 2rem;
            }
            
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.5); }
                70% { box-shadow: 0 0 0 20px rgba(220, 53, 69, 0); }
                100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
            }
            
            .speech-wave {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 3px;
                height: 30px;
                opacity: 0;
                transition: opacity 0.3s;
            }
            
            .speech-wave.active {
                opacity: 1;
            }
            
            .speech-wave::before,
            .speech-wave::after,
            .speech-wave span {
                content: '';
                display: block;
                width: 4px;
                height: 20px;
                background: #F47C26;
                border-radius: 2px;
                animation: wave 0.5s ease-in-out infinite;
            }
            
            .speech-wave::before { animation-delay: 0s; }
            .speech-wave span { animation-delay: 0.1s; }
            .speech-wave::after { animation-delay: 0.2s; }
            
            @keyframes wave {
                0%, 100% { transform: scaleY(0.5); }
                50% { transform: scaleY(1); }
            }
            
            .speech-status {
                font-size: 0.9rem;
                color: #666;
                min-height: 24px;
                text-align: center;
            }
        `;

        document.head.appendChild(styles);
    },

    /**
     * Get user-friendly error message
     */
    getErrorMessage(error) {
        const messages = {
            'no-speech': 'Không nghe thấy giọng nói',
            'audio-capture': 'Không thể truy cập microphone',
            'not-allowed': 'Quyền microphone bị từ chối',
            'network': 'Lỗi kết nối mạng',
            'aborted': 'Đã hủy',
            'language-not-supported': 'Ngôn ngữ không được hỗ trợ'
        };
        return messages[error] || 'Có lỗi xảy ra';
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    /**
     * Check if supported
     */
    isSupported() {
        return this.state.isSupported;
    },

    /**
     * Check if currently listening
     */
    isListening() {
        return this.state.isListening;
    },

    /**
     * Get current transcript
     */
    getTranscript() {
        return this.state.transcript;
    },

    /**
     * Get last confidence score
     */
    getConfidence() {
        return this.state.confidence;
    },

    /**
     * Debug log
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[SpeechRecognizer]', ...args);
        }
    }
};

// Export
window.SpeechRecognizer = SpeechRecognizer;

console.log('[Speech Recognizer] Module loaded');
