/* ====================================
   AUDIO PLAYER - Custom Audio Controls
   Phase 2: Core Features
   Version: 1.0.0
   ==================================== */

/**
 * AudioPlayer - Enhanced audio player for language learning
 * Features:
 * - Playback speed control
 * - Loop segment (A-B repeat)
 * - Sentence/paragraph navigation
 * - Waveform visualization
 * - Subtitle sync
 */
const AudioPlayer = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        defaultSpeed: 1.0,
        speedOptions: [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        skipSeconds: 5,
        autoReplayCount: 3,
        showWaveform: true,
        debug: true
    },

    // State
    state: {
        audio: null,
        isPlaying: false,
        currentTime: 0,
        duration: 0,
        playbackRate: 1.0,
        volume: 1.0,
        isMuted: false,
        loopStart: null,
        loopEnd: null,
        isLooping: false,
        autoReplayRemaining: 0,
        segments: [],
        currentSegment: -1,
        subtitles: [],
        currentSubtitle: null
    },

    // DOM Elements
    elements: {
        container: null,
        audio: null,
        playBtn: null,
        progress: null,
        progressBar: null,
        timeDisplay: null,
        speedBtn: null,
        volumeSlider: null,
        waveform: null,
        subtitleDisplay: null
    },

    // Event callbacks
    callbacks: {
        onPlay: null,
        onPause: null,
        onEnded: null,
        onTimeUpdate: null,
        onSegmentChange: null,
        onSubtitleChange: null
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize the audio player
     * @param {string|HTMLElement} container - Container element or selector
     * @param {Object} options - Configuration options
     */
    init(container, options = {}) {
        this.config = { ...this.config, ...options };
        
        // Get container
        if (typeof container === 'string') {
            this.elements.container = document.querySelector(container);
        } else {
            this.elements.container = container;
        }

        if (!this.elements.container) {
            console.error('[AudioPlayer] Container not found');
            return null;
        }

        // Create player UI
        this.createPlayerUI();
        
        // Setup audio element
        this.setupAudio();
        
        // Bind events
        this.bindEvents();

        this.log('Audio Player initialized');
        return this;
    },

    /**
     * Create player UI
     */
    createPlayerUI() {
        const html = `
            <div class="audio-player" data-player>
                <audio class="audio-element" preload="metadata"></audio>
                
                <!-- Waveform / Progress -->
                <div class="player-waveform">
                    <div class="waveform-bg"></div>
                    <div class="waveform-progress"></div>
                    <div class="loop-region" style="display: none;"></div>
                </div>
                
                <!-- Progress Bar -->
                <div class="player-progress">
                    <div class="progress-bar">
                        <div class="progress-loaded"></div>
                        <div class="progress-played"></div>
                        <div class="progress-handle"></div>
                    </div>
                </div>
                
                <!-- Controls -->
                <div class="player-controls">
                    <div class="controls-left">
                        <button class="btn-player btn-skip-back" title="Lùi 5s">
                            <i class="fas fa-backward"></i>
                        </button>
                        <button class="btn-player btn-play" title="Phát/Dừng">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn-player btn-skip-forward" title="Tiến 5s">
                            <i class="fas fa-forward"></i>
                        </button>
                    </div>
                    
                    <div class="controls-center">
                        <span class="time-current">0:00</span>
                        <span class="time-separator">/</span>
                        <span class="time-total">0:00</span>
                    </div>
                    
                    <div class="controls-right">
                        <button class="btn-player btn-loop" title="Lặp A-B">
                            <i class="fas fa-repeat"></i>
                        </button>
                        <button class="btn-player btn-speed" title="Tốc độ">
                            1x
                        </button>
                        <div class="volume-control">
                            <button class="btn-player btn-volume" title="Âm lượng">
                                <i class="fas fa-volume-up"></i>
                            </button>
                            <input type="range" class="volume-slider" min="0" max="100" value="100">
                        </div>
                    </div>
                </div>
                
                <!-- Subtitle Display -->
                <div class="player-subtitle"></div>
                
                <!-- Speed Menu -->
                <div class="speed-menu" style="display: none;">
                    ${this.config.speedOptions.map(s => 
                        `<button class="speed-option ${s === 1 ? 'active' : ''}" data-speed="${s}">${s}x</button>`
                    ).join('')}
                </div>
            </div>
        `;

        this.elements.container.innerHTML = html;

        // Cache element references
        this.elements.audio = this.elements.container.querySelector('.audio-element');
        this.elements.playBtn = this.elements.container.querySelector('.btn-play');
        this.elements.progressBar = this.elements.container.querySelector('.progress-bar');
        this.elements.progressPlayed = this.elements.container.querySelector('.progress-played');
        this.elements.progressLoaded = this.elements.container.querySelector('.progress-loaded');
        this.elements.timeCurrent = this.elements.container.querySelector('.time-current');
        this.elements.timeTotal = this.elements.container.querySelector('.time-total');
        this.elements.speedBtn = this.elements.container.querySelector('.btn-speed');
        this.elements.speedMenu = this.elements.container.querySelector('.speed-menu');
        this.elements.volumeBtn = this.elements.container.querySelector('.btn-volume');
        this.elements.volumeSlider = this.elements.container.querySelector('.volume-slider');
        this.elements.loopBtn = this.elements.container.querySelector('.btn-loop');
        this.elements.loopRegion = this.elements.container.querySelector('.loop-region');
        this.elements.subtitleDisplay = this.elements.container.querySelector('.player-subtitle');
        this.elements.waveform = this.elements.container.querySelector('.player-waveform');

        // Add styles
        this.injectStyles();
    },

    /**
     * Inject player styles
     */
    injectStyles() {
        if (document.getElementById('audioPlayerStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'audioPlayerStyles';
        styles.textContent = `
            .audio-player {
                background: #fff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                font-family: 'Open Sans', sans-serif;
            }
            
            .player-waveform {
                height: 60px;
                background: #f5f5f5;
                border-radius: 8px;
                margin-bottom: 15px;
                position: relative;
                overflow: hidden;
                cursor: pointer;
            }
            
            .waveform-bg {
                position: absolute;
                inset: 0;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    rgba(244, 124, 38, 0.1) 50%, 
                    transparent 100%
                );
            }
            
            .waveform-progress {
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 0%;
                background: linear-gradient(90deg, 
                    rgba(244, 124, 38, 0.3) 0%, 
                    rgba(244, 124, 38, 0.5) 100%
                );
                transition: width 0.1s linear;
            }
            
            .loop-region {
                position: absolute;
                top: 0;
                bottom: 0;
                background: rgba(244, 124, 38, 0.2);
                border-left: 2px solid #F47C26;
                border-right: 2px solid #F47C26;
            }
            
            .player-progress {
                margin-bottom: 15px;
            }
            
            .progress-bar {
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
                position: relative;
                cursor: pointer;
            }
            
            .progress-loaded {
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                background: #ccc;
                border-radius: 3px;
            }
            
            .progress-played {
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                background: #F47C26;
                border-radius: 3px;
                width: 0%;
            }
            
            .progress-handle {
                position: absolute;
                width: 14px;
                height: 14px;
                background: #F47C26;
                border-radius: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                left: 0%;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                opacity: 0;
                transition: opacity 0.2s;
            }
            
            .progress-bar:hover .progress-handle {
                opacity: 1;
            }
            
            .player-controls {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 15px;
            }
            
            .controls-left, .controls-right {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .controls-center {
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 0.9rem;
                color: #666;
            }
            
            .btn-player {
                width: 40px;
                height: 40px;
                border: none;
                background: #f5f5f5;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
                color: #333;
            }
            
            .btn-player:hover {
                background: #F47C26;
                color: white;
            }
            
            .btn-play {
                width: 50px;
                height: 50px;
                background: #F47C26;
                color: white;
            }
            
            .btn-play:hover {
                background: #D35400;
                transform: scale(1.05);
            }
            
            .btn-speed {
                width: auto;
                padding: 0 12px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.85rem;
            }
            
            .btn-loop.active {
                background: #F47C26;
                color: white;
            }
            
            .volume-control {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .volume-slider {
                width: 80px;
                height: 4px;
                -webkit-appearance: none;
                background: #e0e0e0;
                border-radius: 2px;
                outline: none;
            }
            
            .volume-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                width: 12px;
                height: 12px;
                background: #F47C26;
                border-radius: 50%;
                cursor: pointer;
            }
            
            .speed-menu {
                position: absolute;
                bottom: 100%;
                right: 0;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                padding: 8px;
                display: flex;
                flex-direction: column;
                gap: 4px;
                z-index: 10;
            }
            
            .speed-option {
                padding: 8px 16px;
                border: none;
                background: none;
                cursor: pointer;
                border-radius: 4px;
                text-align: left;
                font-size: 0.9rem;
            }
            
            .speed-option:hover {
                background: #f5f5f5;
            }
            
            .speed-option.active {
                background: #F47C26;
                color: white;
            }
            
            .player-subtitle {
                text-align: center;
                padding: 15px;
                font-size: 1.1rem;
                line-height: 1.6;
                min-height: 60px;
                color: #333;
            }
            
            .player-subtitle .highlight {
                background: rgba(244, 124, 38, 0.2);
                padding: 2px 4px;
                border-radius: 4px;
            }
            
            /* Mobile Responsive */
            @media (max-width: 576px) {
                .audio-player {
                    padding: 15px;
                }
                
                .volume-slider {
                    display: none;
                }
                
                .btn-player {
                    width: 36px;
                    height: 36px;
                }
                
                .btn-play {
                    width: 44px;
                    height: 44px;
                }
            }
        `;

        document.head.appendChild(styles);
    },

    /**
     * Setup audio element
     */
    setupAudio() {
        this.state.audio = this.elements.audio;
    },

    /**
     * Bind event listeners
     */
    bindEvents() {
        const audio = this.state.audio;

        // Audio events
        audio.addEventListener('loadedmetadata', () => this.onLoadedMetadata());
        audio.addEventListener('timeupdate', () => this.onTimeUpdate());
        audio.addEventListener('ended', () => this.onEnded());
        audio.addEventListener('progress', () => this.onProgress());
        audio.addEventListener('play', () => this.onPlay());
        audio.addEventListener('pause', () => this.onPause());

        // Control events
        this.elements.playBtn.addEventListener('click', () => this.togglePlay());
        
        this.elements.container.querySelector('.btn-skip-back').addEventListener('click', () => 
            this.skip(-this.config.skipSeconds)
        );
        this.elements.container.querySelector('.btn-skip-forward').addEventListener('click', () => 
            this.skip(this.config.skipSeconds)
        );

        // Progress bar click
        this.elements.progressBar.addEventListener('click', (e) => this.seekFromClick(e));
        this.elements.waveform?.addEventListener('click', (e) => this.seekFromClick(e, this.elements.waveform));

        // Speed control
        this.elements.speedBtn.addEventListener('click', () => this.toggleSpeedMenu());
        this.elements.speedMenu.querySelectorAll('.speed-option').forEach(btn => {
            btn.addEventListener('click', () => {
                this.setPlaybackRate(parseFloat(btn.dataset.speed));
                this.toggleSpeedMenu(false);
            });
        });

        // Volume control
        this.elements.volumeBtn.addEventListener('click', () => this.toggleMute());
        this.elements.volumeSlider.addEventListener('input', (e) => {
            this.setVolume(e.target.value / 100);
        });

        // Loop control
        this.elements.loopBtn.addEventListener('click', () => this.toggleLoop());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));

        // Close speed menu on outside click
        document.addEventListener('click', (e) => {
            if (!this.elements.speedBtn.contains(e.target) && !this.elements.speedMenu.contains(e.target)) {
                this.toggleSpeedMenu(false);
            }
        });
    },

    // ====================================
    // AUDIO LOADING
    // ====================================
    
    /**
     * Load audio source
     */
    load(src, subtitles = []) {
        this.state.audio.src = src;
        this.state.subtitles = subtitles;
        this.state.currentSegment = -1;
        this.state.loopStart = null;
        this.state.loopEnd = null;
        this.state.isLooping = false;
        
        this.elements.loopBtn.classList.remove('active');
        this.elements.loopRegion.style.display = 'none';
        
        this.log('Loading audio:', src);
    },

    /**
     * Load with segments (for sentence navigation)
     */
    loadWithSegments(src, segments, subtitles = []) {
        this.load(src, subtitles);
        this.state.segments = segments; // Array of { start, end, text }
    },

    // ====================================
    // PLAYBACK CONTROL
    // ====================================
    
    /**
     * Play audio
     */
    play() {
        this.state.audio.play().catch(e => {
            this.log('Play error:', e);
        });
    },

    /**
     * Pause audio
     */
    pause() {
        this.state.audio.pause();
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
     * Stop and reset
     */
    stop() {
        this.pause();
        this.state.audio.currentTime = 0;
    },

    /**
     * Skip forward/backward
     */
    skip(seconds) {
        const newTime = this.state.audio.currentTime + seconds;
        this.seek(Math.max(0, Math.min(newTime, this.state.duration)));
    },

    /**
     * Seek to time
     */
    seek(time) {
        this.state.audio.currentTime = time;
    },

    /**
     * Seek from click event
     */
    seekFromClick(event, element = this.elements.progressBar) {
        const rect = element.getBoundingClientRect();
        const percent = (event.clientX - rect.left) / rect.width;
        this.seek(percent * this.state.duration);
    },

    /**
     * Set playback rate
     */
    setPlaybackRate(rate) {
        this.state.audio.playbackRate = rate;
        this.state.playbackRate = rate;
        this.elements.speedBtn.textContent = rate + 'x';
        
        // Update active state in menu
        this.elements.speedMenu.querySelectorAll('.speed-option').forEach(btn => {
            btn.classList.toggle('active', parseFloat(btn.dataset.speed) === rate);
        });

        this.log('Playback rate:', rate);
    },

    /**
     * Toggle speed menu
     */
    toggleSpeedMenu(show = null) {
        const menu = this.elements.speedMenu;
        const shouldShow = show !== null ? show : menu.style.display === 'none';
        menu.style.display = shouldShow ? 'flex' : 'none';
    },

    /**
     * Set volume
     */
    setVolume(volume) {
        this.state.audio.volume = volume;
        this.state.volume = volume;
        this.state.isMuted = volume === 0;
        this.updateVolumeIcon();
    },

    /**
     * Toggle mute
     */
    toggleMute() {
        if (this.state.isMuted) {
            this.setVolume(this.state.volume || 1);
            this.elements.volumeSlider.value = this.state.volume * 100;
        } else {
            this.state.audio.volume = 0;
            this.state.isMuted = true;
            this.elements.volumeSlider.value = 0;
        }
        this.updateVolumeIcon();
    },

    /**
     * Update volume icon
     */
    updateVolumeIcon() {
        const icon = this.elements.volumeBtn.querySelector('i');
        if (this.state.isMuted || this.state.audio.volume === 0) {
            icon.className = 'fas fa-volume-mute';
        } else if (this.state.audio.volume < 0.5) {
            icon.className = 'fas fa-volume-down';
        } else {
            icon.className = 'fas fa-volume-up';
        }
    },

    // ====================================
    // LOOP (A-B REPEAT)
    // ====================================
    
    /**
     * Toggle loop mode
     */
    toggleLoop() {
        if (!this.state.isLooping) {
            // Start setting loop
            if (this.state.loopStart === null) {
                // Set loop start
                this.state.loopStart = this.state.audio.currentTime;
                this.elements.loopBtn.classList.add('active');
                this.elements.loopBtn.innerHTML = '<i class="fas fa-repeat"></i> A';
                this.log('Loop start set:', this.state.loopStart);
            } else if (this.state.loopEnd === null) {
                // Set loop end
                this.state.loopEnd = this.state.audio.currentTime;
                this.state.isLooping = true;
                this.elements.loopBtn.innerHTML = '<i class="fas fa-repeat"></i>';
                this.showLoopRegion();
                this.log('Loop end set:', this.state.loopEnd);
            }
        } else {
            // Clear loop
            this.clearLoop();
        }
    },

    /**
     * Set loop region
     */
    setLoop(start, end) {
        this.state.loopStart = start;
        this.state.loopEnd = end;
        this.state.isLooping = true;
        this.elements.loopBtn.classList.add('active');
        this.showLoopRegion();
    },

    /**
     * Clear loop
     */
    clearLoop() {
        this.state.loopStart = null;
        this.state.loopEnd = null;
        this.state.isLooping = false;
        this.elements.loopBtn.classList.remove('active');
        this.elements.loopBtn.innerHTML = '<i class="fas fa-repeat"></i>';
        this.elements.loopRegion.style.display = 'none';
    },

    /**
     * Show loop region on waveform
     */
    showLoopRegion() {
        if (!this.state.loopStart || !this.state.loopEnd || !this.state.duration) return;

        const startPercent = (this.state.loopStart / this.state.duration) * 100;
        const endPercent = (this.state.loopEnd / this.state.duration) * 100;
        
        this.elements.loopRegion.style.display = 'block';
        this.elements.loopRegion.style.left = startPercent + '%';
        this.elements.loopRegion.style.width = (endPercent - startPercent) + '%';
    },

    // ====================================
    // SEGMENT NAVIGATION
    // ====================================
    
    /**
     * Go to next segment
     */
    nextSegment() {
        if (this.state.segments.length === 0) return;
        
        const newIndex = Math.min(this.state.currentSegment + 1, this.state.segments.length - 1);
        this.goToSegment(newIndex);
    },

    /**
     * Go to previous segment
     */
    prevSegment() {
        if (this.state.segments.length === 0) return;
        
        const newIndex = Math.max(this.state.currentSegment - 1, 0);
        this.goToSegment(newIndex);
    },

    /**
     * Go to specific segment
     */
    goToSegment(index) {
        if (index < 0 || index >= this.state.segments.length) return;
        
        const segment = this.state.segments[index];
        this.seek(segment.start);
        this.state.currentSegment = index;

        if (this.callbacks.onSegmentChange) {
            this.callbacks.onSegmentChange(segment, index);
        }
    },

    /**
     * Replay current segment
     */
    replaySegment() {
        if (this.state.currentSegment >= 0) {
            this.goToSegment(this.state.currentSegment);
            this.play();
        }
    },

    // ====================================
    // AUTO REPLAY
    // ====================================
    
    /**
     * Start auto replay mode
     */
    startAutoReplay(count = this.config.autoReplayCount) {
        this.state.autoReplayRemaining = count;
        this.play();
    },

    // ====================================
    // SUBTITLE
    // ====================================
    
    /**
     * Update current subtitle
     */
    updateSubtitle() {
        if (this.state.subtitles.length === 0) {
            this.elements.subtitleDisplay.textContent = '';
            return;
        }

        const currentTime = this.state.audio.currentTime;
        const subtitle = this.state.subtitles.find(s => 
            currentTime >= s.start && currentTime <= s.end
        );

        if (subtitle && subtitle !== this.state.currentSubtitle) {
            this.state.currentSubtitle = subtitle;
            this.elements.subtitleDisplay.innerHTML = subtitle.text;

            if (this.callbacks.onSubtitleChange) {
                this.callbacks.onSubtitleChange(subtitle);
            }
        } else if (!subtitle) {
            this.state.currentSubtitle = null;
            this.elements.subtitleDisplay.textContent = '';
        }
    },

    // ====================================
    // EVENT HANDLERS
    // ====================================
    
    onLoadedMetadata() {
        this.state.duration = this.state.audio.duration;
        this.elements.timeTotal.textContent = this.formatTime(this.state.duration);
        this.log('Audio loaded, duration:', this.state.duration);
    },

    onTimeUpdate() {
        this.state.currentTime = this.state.audio.currentTime;
        const percent = (this.state.currentTime / this.state.duration) * 100;
        
        // Update progress
        this.elements.progressPlayed.style.width = percent + '%';
        this.elements.container.querySelector('.progress-handle').style.left = percent + '%';
        
        // Update waveform
        if (this.elements.waveform) {
            this.elements.waveform.querySelector('.waveform-progress').style.width = percent + '%';
        }
        
        // Update time display
        this.elements.timeCurrent.textContent = this.formatTime(this.state.currentTime);
        
        // Update subtitle
        this.updateSubtitle();

        // Check loop
        if (this.state.isLooping && this.state.loopEnd && this.state.currentTime >= this.state.loopEnd) {
            this.seek(this.state.loopStart);
        }

        // Update current segment
        if (this.state.segments.length > 0) {
            for (let i = 0; i < this.state.segments.length; i++) {
                const seg = this.state.segments[i];
                if (this.state.currentTime >= seg.start && this.state.currentTime < seg.end) {
                    if (this.state.currentSegment !== i) {
                        this.state.currentSegment = i;
                        if (this.callbacks.onSegmentChange) {
                            this.callbacks.onSegmentChange(seg, i);
                        }
                    }
                    break;
                }
            }
        }

        if (this.callbacks.onTimeUpdate) {
            this.callbacks.onTimeUpdate(this.state.currentTime, this.state.duration);
        }
    },

    onProgress() {
        if (this.state.audio.buffered.length > 0) {
            const loaded = this.state.audio.buffered.end(0) / this.state.duration * 100;
            this.elements.progressLoaded.style.width = loaded + '%';
        }
    },

    onPlay() {
        this.state.isPlaying = true;
        this.elements.playBtn.querySelector('i').className = 'fas fa-pause';
        
        if (this.callbacks.onPlay) {
            this.callbacks.onPlay();
        }
    },

    onPause() {
        this.state.isPlaying = false;
        this.elements.playBtn.querySelector('i').className = 'fas fa-play';
        
        if (this.callbacks.onPause) {
            this.callbacks.onPause();
        }
    },

    onEnded() {
        this.state.isPlaying = false;
        this.elements.playBtn.querySelector('i').className = 'fas fa-play';

        // Handle auto replay
        if (this.state.autoReplayRemaining > 0) {
            this.state.autoReplayRemaining--;
            this.seek(0);
            this.play();
            return;
        }

        if (this.callbacks.onEnded) {
            this.callbacks.onEnded();
        }
    },

    // ====================================
    // KEYBOARD SHORTCUTS
    // ====================================
    
    handleKeyboard(e) {
        // Only handle if audio player is in focus or globally
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch (e.code) {
            case 'Space':
                e.preventDefault();
                this.togglePlay();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.skip(-5);
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.skip(5);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.setVolume(Math.min(1, this.state.volume + 0.1));
                this.elements.volumeSlider.value = this.state.volume * 100;
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.setVolume(Math.max(0, this.state.volume - 0.1));
                this.elements.volumeSlider.value = this.state.volume * 100;
                break;
            case 'KeyM':
                this.toggleMute();
                break;
            case 'KeyL':
                this.toggleLoop();
                break;
        }
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    /**
     * Format time in MM:SS
     */
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    /**
     * Set callback
     */
    on(event, callback) {
        if (this.callbacks.hasOwnProperty('on' + event.charAt(0).toUpperCase() + event.slice(1))) {
            this.callbacks['on' + event.charAt(0).toUpperCase() + event.slice(1)] = callback;
        }
        return this;
    },

    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    },

    /**
     * Debug log
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[AudioPlayer]', ...args);
        }
    },

    /**
     * Destroy player
     */
    destroy() {
        this.stop();
        this.elements.container.innerHTML = '';
        this.log('Player destroyed');
    }
};

// Export
window.AudioPlayer = AudioPlayer;

console.log('[Audio Player] Module loaded');
