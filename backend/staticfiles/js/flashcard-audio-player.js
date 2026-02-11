/* ====================================
   FLASHCARD AUDIO PLAYER
   Multi-voice TTS with speed control
   Version: 2.0.0 - Phase 2
   ==================================== */

/**
 * FlashcardAudioPlayer - Specialized audio player for flashcard pronunciation
 * 
 * Features:
 * - 4 voice options (US/UK, Male/Female)
 * - 3 speed settings (Slow 70%, Normal, Fast 120%)
 * - Visual feedback (waveform animation)
 * - Auto-play on card flip
 * - Keyboard shortcut (A key)
 * - API integration with backend TTS service
 */
const FlashcardAudioPlayer = {
    // Configuration
    config: {
        apiBaseUrl: '/api/v1/vocabulary',
        voices: {
            us_male: { name: 'US Male', code: 'en-US-GuyNeural', icon: '🇺🇸👨' },
            us_female: { name: 'US Female', code: 'en-US-JennyNeural', icon: '🇺🇸👩' },
            uk_male: { name: 'UK Male', code: 'en-GB-RyanNeural', icon: '🇬🇧👨' },
            uk_female: { name: 'UK Female', code: 'en-GB-SoniaNeural', icon: '🇬🇧👩' }
        },
        speeds: {
            slow: { name: 'Slow (70%)', rate: 0.7, label: '0.7x' },
            normal: { name: 'Normal', rate: 1.0, label: '1x' },
            fast: { name: 'Fast (120%)', rate: 1.2, label: '1.2x' }
        },
        defaultVoice: 'us_male',
        defaultSpeed: 'normal',
        autoPlay: false,
        showWaveform: true
    },

    // State
    state: {
        currentWord: null,
        currentVoice: 'us_male',
        currentSpeed: 'normal',
        audioElement: null,
        isPlaying: false,
        isLoading: false,
        audioCache: new Map() // Cache audio URLs
    },

    // DOM Elements
    elements: {
        container: null,
        audioElement: null,
        playButton: null,
        voiceSelector: null,
        speedSelector: null,
        waveform: null,
        loadingIndicator: null
    },

    /**
     * Initialize the flashcard audio player
     * @param {string|HTMLElement} container - Container element or selector
     * @param {Object} options - Configuration options
     */
    init(container, options = {}) {
        // Merge options
        this.config = { ...this.config, ...options };
        
        // Get container
        if (typeof container === 'string') {
            this.elements.container = document.querySelector(container);
        } else {
            this.elements.container = container;
        }

        if (!this.elements.container) {
            console.error('[FlashcardAudioPlayer] Container not found');
            return null;
        }

        // Load saved preferences
        this.loadPreferences();

        // Create UI
        this.createUI();
        
        // Setup audio element
        this.setupAudio();
        
        // Bind events
        this.bindEvents();

        console.log('[FlashcardAudioPlayer] Initialized');
        return this;
    },

    /**
     * Create player UI
     */
    createUI() {
        const voiceOptions = Object.entries(this.config.voices)
            .map(([key, voice]) => `
                <option value="${key}" ${key === this.state.currentVoice ? 'selected' : ''}>
                    ${voice.icon} ${voice.name}
                </option>
            `).join('');

        const speedOptions = Object.entries(this.config.speeds)
            .map(([key, speed]) => `
                <option value="${key}" ${key === this.state.currentSpeed ? 'selected' : ''}>
                    ${speed.label} ${speed.name}
                </option>
            `).join('');

        const html = `
            <div class="flashcard-audio-player">
                <!-- Audio Element -->
                <audio class="audio-element" preload="auto"></audio>
                
                <!-- Main Controls -->
                <div class="audio-controls">
                    <!-- Play Button -->
                    <button class="btn-audio-play" title="Play pronunciation (A key)" aria-label="Play audio">
                        <i class="fas fa-volume-up"></i>
                        <span class="btn-label">Play</span>
                    </button>
                    
                    <!-- Voice Selection -->
                    <div class="audio-option">
                        <label for="voice-select" class="option-label">
                            <i class="fas fa-user"></i> Voice
                        </label>
                        <select id="voice-select" class="voice-selector form-select form-select-sm">
                            ${voiceOptions}
                        </select>
                    </div>
                    
                    <!-- Speed Control -->
                    <div class="audio-option">
                        <label for="speed-select" class="option-label">
                            <i class="fas fa-gauge"></i> Speed
                        </label>
                        <select id="speed-select" class="speed-selector form-select form-select-sm">
                            ${speedOptions}
                        </select>
                    </div>
                </div>
                
                <!-- Waveform Visualization -->
                ${this.config.showWaveform ? `
                <div class="audio-waveform">
                    <div class="waveform-bars">
                        ${Array(20).fill(0).map((_, i) => `<div class="bar bar-${i}"></div>`).join('')}
                    </div>
                </div>
                ` : ''}
                
                <!-- Loading Indicator -->
                <div class="audio-loading" style="display: none;">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="loading-text">Generating audio...</span>
                </div>
            </div>
        `;

        this.elements.container.innerHTML = html;

        // Cache DOM references
        this.elements.audioElement = this.elements.container.querySelector('.audio-element');
        this.elements.playButton = this.elements.container.querySelector('.btn-audio-play');
        this.elements.voiceSelector = this.elements.container.querySelector('.voice-selector');
        this.elements.speedSelector = this.elements.container.querySelector('.speed-selector');
        this.elements.waveform = this.elements.container.querySelector('.audio-waveform');
        this.elements.loadingIndicator = this.elements.container.querySelector('.audio-loading');
    },

    /**
     * Setup audio element
     */
    setupAudio() {
        if (!this.elements.audioElement) return;

        this.state.audioElement = this.elements.audioElement;

        // Audio event listeners
        this.elements.audioElement.addEventListener('loadstart', () => {
            this.setLoadingState(true);
        });

        this.elements.audioElement.addEventListener('canplay', () => {
            this.setLoadingState(false);
        });

        this.elements.audioElement.addEventListener('play', () => {
            this.state.isPlaying = true;
            this.updatePlayButton();
            this.startWaveformAnimation();
        });

        this.elements.audioElement.addEventListener('pause', () => {
            this.state.isPlaying = false;
            this.updatePlayButton();
            this.stopWaveformAnimation();
        });

        this.elements.audioElement.addEventListener('ended', () => {
            this.state.isPlaying = false;
            this.updatePlayButton();
            this.stopWaveformAnimation();
        });

        this.elements.audioElement.addEventListener('error', (e) => {
            console.error('[FlashcardAudioPlayer] Audio error:', e);
            this.setLoadingState(false);
            this.showError('Failed to load audio');
        });
    },

    /**
     * Bind UI events
     */
    bindEvents() {
        // Play button
        if (this.elements.playButton) {
            this.elements.playButton.addEventListener('click', () => {
                this.togglePlay();
            });
        }

        // Voice selector
        if (this.elements.voiceSelector) {
            this.elements.voiceSelector.addEventListener('change', (e) => {
                this.changeVoice(e.target.value);
            });
        }

        // Speed selector
        if (this.elements.speedSelector) {
            this.elements.speedSelector.addEventListener('change', (e) => {
                this.changeSpeed(e.target.value);
            });
        }

        // Keyboard shortcut (A key for audio)
        document.addEventListener('keydown', (e) => {
            if (e.key.toLowerCase() === 'a' && !e.ctrlKey && !e.metaKey) {
                // Check if not in input field
                if (!['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
                    e.preventDefault();
                    this.togglePlay();
                }
            }
        });
    },

    /**
     * Load audio for a word
     * @param {string} word - Word to pronounce
     * @param {Object} options - Options (voice, speed, autoPlay)
     */
    async loadWord(word, options = {}) {
        if (!word) {
            console.error('[FlashcardAudioPlayer] No word provided');
            return;
        }

        this.state.currentWord = word;
        
        // Apply options
        if (options.voice) {
            this.state.currentVoice = options.voice;
            if (this.elements.voiceSelector) {
                this.elements.voiceSelector.value = options.voice;
            }
        }
        
        if (options.speed) {
            this.state.currentSpeed = options.speed;
            if (this.elements.speedSelector) {
                this.elements.speedSelector.value = options.speed;
            }
        }

        // Get audio URL
        const audioUrl = await this.getAudioUrl(word, this.state.currentVoice, this.state.currentSpeed);
        
        if (audioUrl) {
            // Load audio
            this.elements.audioElement.src = audioUrl;
            this.elements.audioElement.load();

            // Auto-play if enabled
            if (options.autoPlay || this.config.autoPlay) {
                setTimeout(() => {
                    this.play();
                }, 100);
            }
        }
    },

    /**
     * Get audio URL from API or cache
     * @param {string} word - Word
     * @param {string} voice - Voice ID
     * @param {string} speed - Speed ID
     * @returns {Promise<string|null>} Audio URL
     */
    async getAudioUrl(word, voice, speed) {
        // Check cache first
        const cacheKey = `${word}_${voice}_${speed}`;
        if (this.state.audioCache.has(cacheKey)) {
            console.log('[FlashcardAudioPlayer] Audio from cache');
            return this.state.audioCache.get(cacheKey);
        }

        try {
            this.setLoadingState(true);

            // Call API to generate/get audio
            const response = await fetch(`${this.config.apiBaseUrl}/audio/generate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    word: word,
                    voice: voice,
                    speed: speed,
                    async: false  // Synchronous generation
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.audio_url) {
                // Cache the URL
                this.state.audioCache.set(cacheKey, data.audio_url);
                return data.audio_url;
            } else {
                throw new Error('No audio URL in response');
            }

        } catch (error) {
            console.error('[FlashcardAudioPlayer] Error fetching audio:', error);
            this.showError('Failed to load audio');
            return null;
        } finally {
            this.setLoadingState(false);
        }
    },

    /**
     * Play audio
     */
    async play() {
        if (!this.elements.audioElement.src) {
            console.warn('[FlashcardAudioPlayer] No audio loaded');
            return;
        }

        try {
            await this.elements.audioElement.play();
        } catch (error) {
            console.error('[FlashcardAudioPlayer] Playback error:', error);
        }
    },

    /**
     * Pause audio
     */
    pause() {
        this.elements.audioElement.pause();
    },

    /**
     * Toggle play/pause
     */
    togglePlay() {
        if (this.state.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    },

    /**
     * Change voice
     * @param {string} voiceId - Voice ID (us_male, us_female, etc.)
     */
    async changeVoice(voiceId) {
        if (!this.config.voices[voiceId]) {
            console.error('[FlashcardAudioPlayer] Invalid voice:', voiceId);
            return;
        }

        this.state.currentVoice = voiceId;
        this.savePreferences();

        // Reload current word with new voice
        if (this.state.currentWord) {
            await this.loadWord(this.state.currentWord);
        }

        console.log('[FlashcardAudioPlayer] Voice changed to:', voiceId);
    },

    /**
     * Change speed
     * @param {string} speedId - Speed ID (slow, normal, fast)
     */
    async changeSpeed(speedId) {
        if (!this.config.speeds[speedId]) {
            console.error('[FlashcardAudioPlayer] Invalid speed:', speedId);
            return;
        }

        this.state.currentSpeed = speedId;
        this.savePreferences();

        // Reload current word with new speed
        if (this.state.currentWord) {
            await this.loadWord(this.state.currentWord);
        }

        console.log('[FlashcardAudioPlayer] Speed changed to:', speedId);
    },

    /**
     * Update play button UI
     */
    updatePlayButton() {
        if (!this.elements.playButton) return;

        const icon = this.elements.playButton.querySelector('i');
        const label = this.elements.playButton.querySelector('.btn-label');

        if (this.state.isPlaying) {
            icon.className = 'fas fa-pause';
            label.textContent = 'Pause';
            this.elements.playButton.classList.add('playing');
        } else {
            icon.className = 'fas fa-volume-up';
            label.textContent = 'Play';
            this.elements.playButton.classList.remove('playing');
        }
    },

    /**
     * Set loading state
     * @param {boolean} isLoading - Loading state
     */
    setLoadingState(isLoading) {
        this.state.isLoading = isLoading;

        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = isLoading ? 'flex' : 'none';
        }

        if (this.elements.playButton) {
            this.elements.playButton.disabled = isLoading;
        }
    },

    /**
     * Start waveform animation
     */
    startWaveformAnimation() {
        if (!this.elements.waveform) return;

        const bars = this.elements.waveform.querySelectorAll('.bar');
        bars.forEach((bar, index) => {
            bar.style.animationDelay = `${index * 0.05}s`;
            bar.classList.add('animating');
        });
    },

    /**
     * Stop waveform animation
     */
    stopWaveformAnimation() {
        if (!this.elements.waveform) return;

        const bars = this.elements.waveform.querySelectorAll('.bar');
        bars.forEach(bar => {
            bar.classList.remove('animating');
        });
    },

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // Create toast notification
        if (typeof showToast === 'function') {
            showToast(message, 'error');
        } else {
            alert(message);
        }
    },

    /**
     * Get auth token from localStorage
     * @returns {string|null} JWT token
     */
    getAuthToken() {
        return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    },

    /**
     * Save user preferences
     */
    savePreferences() {
        const preferences = {
            voice: this.state.currentVoice,
            speed: this.state.currentSpeed
        };
        localStorage.setItem('flashcard_audio_preferences', JSON.stringify(preferences));
    },

    /**
     * Load user preferences
     */
    loadPreferences() {
        try {
            const saved = localStorage.getItem('flashcard_audio_preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                this.state.currentVoice = preferences.voice || this.config.defaultVoice;
                this.state.currentSpeed = preferences.speed || this.config.defaultSpeed;
            }
        } catch (error) {
            console.error('[FlashcardAudioPlayer] Error loading preferences:', error);
        }
    },

    /**
     * Clear audio cache
     */
    clearCache() {
        this.state.audioCache.clear();
        console.log('[FlashcardAudioPlayer] Cache cleared');
    },

    /**
     * Destroy player
     */
    destroy() {
        // Stop playback
        if (this.elements.audioElement) {
            this.elements.audioElement.pause();
            this.elements.audioElement.src = '';
        }

        // Clear cache
        this.clearCache();

        // Remove UI
        if (this.elements.container) {
            this.elements.container.innerHTML = '';
        }

        console.log('[FlashcardAudioPlayer] Destroyed');
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlashcardAudioPlayer;
}
