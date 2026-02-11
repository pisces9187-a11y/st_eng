/* ====================================
   WRITING ANALYZER - Text Analysis Engine
   Phase 3: Advanced Features
   Version: 1.0.0
   ==================================== */

/**
 * WritingAnalyzer - Comprehensive writing analysis tool
 * Features:
 * - Word and character count
 * - Readability metrics
 * - Vocabulary diversity analysis
 * - Writing style feedback
 * - Error detection patterns
 * - AI-powered suggestions
 */
const WritingAnalyzer = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        minWordsForAnalysis: 20,
        targetLevel: 'B1',          // A1, A2, B1, B2, C1, C2
        enableAutoSave: true,
        autoSaveInterval: 30000,
        enableRealTimeAnalysis: true,
        analysisDelay: 1000,        // Debounce delay
        debug: true
    },

    // CEFR Level word lists (simplified)
    levelVocabulary: {
        A1: ['the', 'is', 'are', 'am', 'was', 'were', 'have', 'has', 'do', 'does', 'go', 'come', 'like', 'want', 'need', 'see', 'know', 'think', 'good', 'bad', 'big', 'small', 'new', 'old', 'time', 'day', 'year', 'people', 'way', 'thing'],
        A2: ['because', 'although', 'however', 'also', 'already', 'always', 'never', 'sometimes', 'usually', 'often', 'important', 'different', 'possible', 'necessary', 'available', 'believe', 'understand', 'remember', 'forget', 'decide'],
        B1: ['therefore', 'moreover', 'furthermore', 'nevertheless', 'consequently', 'meanwhile', 'alternatively', 'significantly', 'approximately', 'predominantly', 'influence', 'opportunity', 'environment', 'development', 'responsibility'],
        B2: ['notwithstanding', 'henceforth', 'thereby', 'whereby', 'nonetheless', 'subsequently', 'simultaneously', 'predominantly', 'substantially', 'unprecedented', 'comprehensive', 'sophisticated', 'implications', 'perspective'],
        C1: ['paradoxically', 'quintessentially', 'unequivocally', 'idiosyncratic', 'paradigmatic', 'concomitant', 'commensurate', 'dichotomy', 'juxtaposition', 'nomenclature', 'epistemological', 'ontological'],
        C2: ['verisimilitude', 'perspicacious', 'magnanimous', 'sycophantic', 'pusillanimous', 'obsequious', 'antediluvian', 'sesquipedalian', 'tergiversation', 'defenestration']
    },

    // Common errors patterns
    commonErrors: [
        { pattern: /\bi am agree\b/gi, suggestion: 'I agree', type: 'grammar' },
        { pattern: /\bmore better\b/gi, suggestion: 'better', type: 'grammar' },
        { pattern: /\bmore worse\b/gi, suggestion: 'worse', type: 'grammar' },
        { pattern: /\bvery much\s+\w+er\b/gi, suggestion: 'much [comparative]', type: 'grammar' },
        { pattern: /\bdepends of\b/gi, suggestion: 'depends on', type: 'preposition' },
        { pattern: /\bdifferent of\b/gi, suggestion: 'different from', type: 'preposition' },
        { pattern: /\bgood in\b/gi, suggestion: 'good at', type: 'preposition' },
        { pattern: /\binterested for\b/gi, suggestion: 'interested in', type: 'preposition' },
        { pattern: /\bhe go\b/gi, suggestion: 'he goes', type: 'subject-verb' },
        { pattern: /\bshe go\b/gi, suggestion: 'she goes', type: 'subject-verb' },
        { pattern: /\bit go\b/gi, suggestion: 'it goes', type: 'subject-verb' },
        { pattern: /\bpeoples\b/gi, suggestion: 'people', type: 'plural' },
        { pattern: /\binformations\b/gi, suggestion: 'information', type: 'uncountable' },
        { pattern: /\badvices\b/gi, suggestion: 'advice', type: 'uncountable' },
        { pattern: /\bfurnitures\b/gi, suggestion: 'furniture', type: 'uncountable' },
        { pattern: /\bequipments\b/gi, suggestion: 'equipment', type: 'uncountable' },
        { pattern: /\s{2,}/g, suggestion: ' ', type: 'formatting' },
        { pattern: /\.\s*,/g, suggestion: '.', type: 'punctuation' },
        { pattern: /,\s*\./g, suggestion: '.', type: 'punctuation' }
    ],

    // Transition words for analysis
    transitionWords: {
        addition: ['also', 'furthermore', 'moreover', 'additionally', 'besides', 'in addition'],
        contrast: ['however', 'but', 'although', 'nevertheless', 'on the other hand', 'despite', 'whereas'],
        cause: ['because', 'since', 'as a result', 'therefore', 'consequently', 'thus', 'hence'],
        example: ['for example', 'for instance', 'such as', 'namely', 'specifically'],
        conclusion: ['in conclusion', 'finally', 'in summary', 'to sum up', 'overall', 'therefore']
    },

    // State
    state: {
        text: '',
        analysis: null,
        errors: [],
        suggestions: [],
        autoSaveTimer: null,
        analysisTimer: null
    },

    // DOM Elements
    elements: {
        container: null,
        textarea: null,
        statsPanel: null,
        errorsPanel: null,
        suggestionsPanel: null
    },

    // Callbacks
    callbacks: {
        onAnalysisComplete: null,
        onAutoSave: null,
        onError: null
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize writing analyzer
     */
    init(container, options = {}) {
        this.config = { ...this.config, ...options };

        if (typeof container === 'string') {
            this.elements.container = document.querySelector(container);
        } else {
            this.elements.container = container;
        }

        if (!this.elements.container) {
            console.error('[WritingAnalyzer] Container not found');
            return null;
        }

        this.log('Writing Analyzer initialized');
        return this;
    },

    /**
     * Create writing UI
     */
    createUI(options = {}) {
        const html = `
            <div class="writing-analyzer">
                <!-- Header -->
                <div class="wa-header">
                    <div class="wa-title">
                        <h3><i class="fas fa-pen-fancy"></i> Luyện Viết</h3>
                        <span class="wa-level-badge level-${this.config.targetLevel.toLowerCase()}">${this.config.targetLevel}</span>
                    </div>
                    <div class="wa-actions">
                        <button class="wa-btn wa-btn-analyze">
                            <i class="fas fa-search"></i> Phân tích
                        </button>
                        <button class="wa-btn wa-btn-clear">
                            <i class="fas fa-eraser"></i> Xóa
                        </button>
                    </div>
                </div>

                <!-- Writing Area -->
                <div class="wa-main">
                    <div class="wa-editor-section">
                        ${options.prompt ? `
                            <div class="wa-prompt">
                                <h4><i class="fas fa-question-circle"></i> Đề bài</h4>
                                <p>${options.prompt}</p>
                            </div>
                        ` : ''}
                        
                        <div class="wa-editor-wrapper">
                            <textarea 
                                class="wa-textarea" 
                                placeholder="${options.placeholder || 'Viết bài của bạn tại đây...'}"
                                spellcheck="false"
                            >${this.state.text}</textarea>
                            
                            <div class="wa-live-stats">
                                <span class="stat-words"><i class="fas fa-font"></i> <span>0</span> từ</span>
                                <span class="stat-chars"><i class="fas fa-text-width"></i> <span>0</span> ký tự</span>
                                <span class="stat-sentences"><i class="fas fa-align-left"></i> <span>0</span> câu</span>
                            </div>
                        </div>
                    </div>

                    <!-- Analysis Panel -->
                    <div class="wa-analysis-panel" style="display: none;">
                        <!-- Overview -->
                        <div class="wa-section wa-overview">
                            <h4><i class="fas fa-chart-pie"></i> Tổng quan</h4>
                            <div class="wa-overview-content"></div>
                        </div>

                        <!-- Score -->
                        <div class="wa-section wa-score-section">
                            <h4><i class="fas fa-star"></i> Điểm đánh giá</h4>
                            <div class="wa-score-content"></div>
                        </div>

                        <!-- Readability -->
                        <div class="wa-section wa-readability">
                            <h4><i class="fas fa-glasses"></i> Độ dễ đọc</h4>
                            <div class="wa-readability-content"></div>
                        </div>

                        <!-- Vocabulary -->
                        <div class="wa-section wa-vocabulary">
                            <h4><i class="fas fa-book"></i> Từ vựng</h4>
                            <div class="wa-vocabulary-content"></div>
                        </div>

                        <!-- Errors -->
                        <div class="wa-section wa-errors">
                            <h4><i class="fas fa-exclamation-triangle"></i> Lỗi phát hiện</h4>
                            <div class="wa-errors-content"></div>
                        </div>

                        <!-- Suggestions -->
                        <div class="wa-section wa-suggestions">
                            <h4><i class="fas fa-lightbulb"></i> Gợi ý cải thiện</h4>
                            <div class="wa-suggestions-content"></div>
                        </div>
                    </div>
                </div>
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
        this.elements.textarea = c.querySelector('.wa-textarea');
        this.elements.analyzeBtn = c.querySelector('.wa-btn-analyze');
        this.elements.clearBtn = c.querySelector('.wa-btn-clear');
        this.elements.analysisPanel = c.querySelector('.wa-analysis-panel');
        this.elements.liveStats = {
            words: c.querySelector('.stat-words span'),
            chars: c.querySelector('.stat-chars span'),
            sentences: c.querySelector('.stat-sentences span')
        };
        this.elements.sections = {
            overview: c.querySelector('.wa-overview-content'),
            score: c.querySelector('.wa-score-content'),
            readability: c.querySelector('.wa-readability-content'),
            vocabulary: c.querySelector('.wa-vocabulary-content'),
            errors: c.querySelector('.wa-errors-content'),
            suggestions: c.querySelector('.wa-suggestions-content')
        };
    },

    /**
     * Bind events
     */
    bindEvents() {
        // Text input
        this.elements.textarea.addEventListener('input', (e) => {
            this.state.text = e.target.value;
            this.updateLiveStats();
            
            if (this.config.enableRealTimeAnalysis) {
                this.scheduleAnalysis();
            }
        });

        // Analyze button
        this.elements.analyzeBtn.addEventListener('click', () => {
            this.analyze();
        });

        // Clear button
        this.elements.clearBtn.addEventListener('click', () => {
            this.clear();
        });

        // Auto-save
        if (this.config.enableAutoSave) {
            this.startAutoSave();
        }
    },

    /**
     * Inject styles
     */
    injectStyles() {
        if (document.getElementById('writingAnalyzerStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'writingAnalyzerStyles';
        styles.textContent = `
            .writing-analyzer {
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            }
            
            .wa-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 24px;
                background: linear-gradient(135deg, #183B56 0%, #2C5F7C 100%);
                color: white;
            }
            
            .wa-title {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .wa-title h3 {
                margin: 0;
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
            }
            
            .wa-level-badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            
            .level-a1, .level-a2 { background: #27AE60; }
            .level-b1, .level-b2 { background: #F47C26; }
            .level-c1, .level-c2 { background: #9B59B6; }
            
            .wa-actions {
                display: flex;
                gap: 12px;
            }
            
            .wa-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .wa-btn-analyze {
                background: #F47C26;
                color: white;
            }
            
            .wa-btn-analyze:hover {
                background: #D35400;
            }
            
            .wa-btn-clear {
                background: rgba(255, 255, 255, 0.2);
                color: white;
            }
            
            .wa-btn-clear:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            .wa-main {
                display: grid;
                grid-template-columns: 1fr 380px;
                min-height: 500px;
            }
            
            .wa-editor-section {
                padding: 24px;
                border-right: 1px solid #E0E6ED;
            }
            
            .wa-prompt {
                margin-bottom: 20px;
                padding: 16px;
                background: #FFF9E6;
                border-radius: 12px;
                border-left: 4px solid #FFC107;
            }
            
            .wa-prompt h4 {
                margin: 0 0 8px 0;
                font-size: 0.9rem;
                color: #183B56;
            }
            
            .wa-prompt p {
                margin: 0;
                color: #555;
            }
            
            .wa-editor-wrapper {
                position: relative;
            }
            
            .wa-textarea {
                width: 100%;
                min-height: 350px;
                padding: 20px;
                border: 2px solid #E0E6ED;
                border-radius: 12px;
                font-size: 1rem;
                line-height: 1.8;
                resize: vertical;
                font-family: 'Open Sans', sans-serif;
                transition: border-color 0.3s ease;
            }
            
            .wa-textarea:focus {
                outline: none;
                border-color: #F47C26;
            }
            
            .wa-live-stats {
                display: flex;
                gap: 20px;
                padding: 12px 0;
                color: #6c757d;
                font-size: 0.9rem;
            }
            
            .wa-live-stats span {
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .wa-live-stats span span {
                font-weight: 600;
                color: #183B56;
            }
            
            .wa-analysis-panel {
                padding: 20px;
                background: #F9FAFC;
                max-height: 550px;
                overflow-y: auto;
            }
            
            .wa-section {
                background: white;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 16px;
            }
            
            .wa-section h4 {
                margin: 0 0 12px 0;
                font-size: 0.95rem;
                color: #183B56;
                font-family: 'Montserrat', sans-serif;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .wa-section h4 i {
                color: #F47C26;
            }
            
            /* Score Display */
            .score-circle {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 12px;
                font-family: 'Montserrat', sans-serif;
                font-size: 2rem;
                font-weight: 800;
                color: white;
            }
            
            .score-excellent { background: linear-gradient(135deg, #27AE60, #2ECC71); }
            .score-good { background: linear-gradient(135deg, #3498DB, #5DADE2); }
            .score-fair { background: linear-gradient(135deg, #F47C26, #F39C12); }
            .score-poor { background: linear-gradient(135deg, #E74C3C, #EC7063); }
            
            /* Stats Grid */
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }
            
            .stat-box {
                text-align: center;
                padding: 12px;
                background: #F9FAFC;
                border-radius: 8px;
            }
            
            .stat-box-value {
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
                font-size: 1.5rem;
                color: #183B56;
            }
            
            .stat-box-label {
                font-size: 0.75rem;
                color: #6c757d;
            }
            
            /* Readability Bar */
            .readability-bar {
                height: 8px;
                background: #E0E6ED;
                border-radius: 4px;
                margin: 8px 0;
                overflow: hidden;
            }
            
            .readability-fill {
                height: 100%;
                background: #F47C26;
                transition: width 0.5s ease;
            }
            
            .readability-labels {
                display: flex;
                justify-content: space-between;
                font-size: 0.75rem;
                color: #6c757d;
            }
            
            /* Vocabulary Pills */
            .vocab-level {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 8px;
            }
            
            .vocab-pill {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
            }
            
            .vocab-pill.a1-a2 { background: #E8F5E9; color: #27AE60; }
            .vocab-pill.b1-b2 { background: #FFF3E0; color: #F47C26; }
            .vocab-pill.c1-c2 { background: #F3E5F5; color: #9B59B6; }
            
            /* Error List */
            .error-item {
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                border-left: 4px solid #E74C3C;
                background: #FFEBEE;
            }
            
            .error-item-type {
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                color: #E74C3C;
                margin-bottom: 4px;
            }
            
            .error-item-text {
                color: #333;
                margin-bottom: 4px;
            }
            
            .error-item-suggestion {
                font-size: 0.85rem;
                color: #27AE60;
            }
            
            /* Suggestions */
            .suggestion-item {
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                background: #E3F2FD;
                border-left: 4px solid #3498DB;
            }
            
            .suggestion-icon {
                color: #3498DB;
                margin-right: 8px;
            }
            
            /* No results */
            .no-results {
                text-align: center;
                padding: 20px;
                color: #6c757d;
            }
            
            /* Mobile */
            @media (max-width: 768px) {
                .wa-main {
                    grid-template-columns: 1fr;
                }
                
                .wa-editor-section {
                    border-right: none;
                    border-bottom: 1px solid #E0E6ED;
                }
                
                .wa-analysis-panel {
                    max-height: none;
                }
                
                .wa-header {
                    flex-direction: column;
                    gap: 16px;
                }
            }
        `;

        document.head.appendChild(styles);
    },

    // ====================================
    // ANALYSIS
    // ====================================
    
    /**
     * Schedule analysis with debounce
     */
    scheduleAnalysis() {
        if (this.state.analysisTimer) {
            clearTimeout(this.state.analysisTimer);
        }

        this.state.analysisTimer = setTimeout(() => {
            if (this.getWordCount() >= this.config.minWordsForAnalysis) {
                this.analyze();
            }
        }, this.config.analysisDelay);
    },

    /**
     * Perform full analysis
     */
    analyze() {
        const text = this.state.text.trim();
        
        if (!text || this.getWordCount() < this.config.minWordsForAnalysis) {
            this.showNotEnoughText();
            return null;
        }

        const analysis = {
            basic: this.analyzeBasicStats(text),
            readability: this.analyzeReadability(text),
            vocabulary: this.analyzeVocabulary(text),
            structure: this.analyzeStructure(text),
            errors: this.findErrors(text),
            suggestions: this.generateSuggestions(text),
            score: 0
        };

        // Calculate overall score
        analysis.score = this.calculateScore(analysis);
        
        this.state.analysis = analysis;
        this.renderAnalysis(analysis);

        if (this.callbacks.onAnalysisComplete) {
            this.callbacks.onAnalysisComplete(analysis);
        }

        this.log('Analysis complete:', analysis);
        return analysis;
    },

    /**
     * Analyze basic statistics
     */
    analyzeBasicStats(text) {
        const words = text.split(/\s+/).filter(w => w.length > 0);
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        const paragraphs = text.split(/\n\n+/).filter(p => p.trim().length > 0);
        
        const wordLengths = words.map(w => w.replace(/[^\w]/g, '').length);
        const avgWordLength = wordLengths.reduce((a, b) => a + b, 0) / words.length || 0;
        const avgSentenceLength = words.length / sentences.length || 0;

        return {
            characters: text.length,
            charactersNoSpaces: text.replace(/\s/g, '').length,
            words: words.length,
            sentences: sentences.length,
            paragraphs: paragraphs.length,
            avgWordLength: avgWordLength.toFixed(1),
            avgSentenceLength: avgSentenceLength.toFixed(1)
        };
    },

    /**
     * Analyze readability
     */
    analyzeReadability(text) {
        const words = text.split(/\s+/).filter(w => w.length > 0);
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        
        const syllables = words.reduce((sum, word) => sum + this.countSyllables(word), 0);
        
        // Flesch Reading Ease
        const ASL = words.length / sentences.length;
        const ASW = syllables / words.length;
        const fleschScore = 206.835 - (1.015 * ASL) - (84.6 * ASW);
        
        // Flesch-Kincaid Grade Level
        const gradeLevel = (0.39 * ASL) + (11.8 * ASW) - 15.59;

        return {
            fleschScore: Math.min(100, Math.max(0, Math.round(fleschScore))),
            gradeLevel: Math.max(0, gradeLevel.toFixed(1)),
            level: this.getReadabilityLevel(fleschScore),
            description: this.getReadabilityDescription(fleschScore)
        };
    },

    /**
     * Count syllables in a word
     */
    countSyllables(word) {
        word = word.toLowerCase().replace(/[^a-z]/g, '');
        if (word.length <= 3) return 1;
        
        word = word.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '');
        word = word.replace(/^y/, '');
        
        const matches = word.match(/[aeiouy]{1,2}/g);
        return matches ? matches.length : 1;
    },

    /**
     * Analyze vocabulary
     */
    analyzeVocabulary(text) {
        const words = text.toLowerCase().split(/\s+/)
            .map(w => w.replace(/[^\w]/g, ''))
            .filter(w => w.length > 2);
        
        const uniqueWords = [...new Set(words)];
        const diversity = (uniqueWords.length / words.length) * 100 || 0;

        // Check vocabulary level distribution
        const levelDistribution = {
            basic: 0,      // A1-A2
            intermediate: 0, // B1-B2
            advanced: 0     // C1-C2
        };

        uniqueWords.forEach(word => {
            if ([...this.levelVocabulary.A1, ...this.levelVocabulary.A2].includes(word)) {
                levelDistribution.basic++;
            } else if ([...this.levelVocabulary.B1, ...this.levelVocabulary.B2].includes(word)) {
                levelDistribution.intermediate++;
            } else if ([...this.levelVocabulary.C1, ...this.levelVocabulary.C2].includes(word)) {
                levelDistribution.advanced++;
            }
        });

        // Find transition words used
        const transitionsUsed = [];
        Object.entries(this.transitionWords).forEach(([type, words]) => {
            words.forEach(tw => {
                if (text.toLowerCase().includes(tw)) {
                    transitionsUsed.push({ word: tw, type });
                }
            });
        });

        return {
            totalWords: words.length,
            uniqueWords: uniqueWords.length,
            diversity: diversity.toFixed(1),
            levelDistribution,
            transitionsUsed,
            advancedWords: this.findAdvancedWords(uniqueWords)
        };
    },

    /**
     * Find advanced words
     */
    findAdvancedWords(words) {
        const advanced = [];
        const advancedList = [...this.levelVocabulary.B2, ...this.levelVocabulary.C1, ...this.levelVocabulary.C2];
        
        words.forEach(word => {
            if (advancedList.includes(word) || word.length >= 10) {
                advanced.push(word);
            }
        });

        return advanced.slice(0, 10);
    },

    /**
     * Analyze structure
     */
    analyzeStructure(text) {
        const paragraphs = text.split(/\n\n+/).filter(p => p.trim().length > 0);
        const hasIntro = paragraphs.length >= 1;
        const hasBody = paragraphs.length >= 2;
        const hasConclusion = paragraphs.length >= 3 && 
            /in conclusion|finally|to sum up|overall|therefore/i.test(paragraphs[paragraphs.length - 1]);

        return {
            paragraphs: paragraphs.length,
            hasIntro,
            hasBody,
            hasConclusion,
            structureScore: ((hasIntro ? 1 : 0) + (hasBody ? 1 : 0) + (hasConclusion ? 1 : 0)) / 3 * 100
        };
    },

    /**
     * Find errors in text
     */
    findErrors(text) {
        const errors = [];

        this.commonErrors.forEach(error => {
            const matches = text.match(error.pattern);
            if (matches) {
                matches.forEach(match => {
                    errors.push({
                        text: match,
                        suggestion: error.suggestion,
                        type: error.type
                    });
                });
            }
        });

        return errors;
    },

    /**
     * Generate suggestions
     */
    generateSuggestions(text) {
        const suggestions = [];
        const analysis = {
            basic: this.analyzeBasicStats(text),
            vocabulary: this.analyzeVocabulary(text),
            structure: this.analyzeStructure(text)
        };

        // Sentence length suggestions
        if (analysis.basic.avgSentenceLength > 25) {
            suggestions.push({
                icon: 'fa-cut',
                text: 'Câu văn có vẻ dài. Cân nhắc chia thành các câu ngắn hơn để dễ đọc.'
            });
        }

        // Vocabulary diversity
        if (analysis.vocabulary.diversity < 40) {
            suggestions.push({
                icon: 'fa-book',
                text: 'Sử dụng thêm từ vựng đa dạng để bài viết phong phú hơn.'
            });
        }

        // Transitions
        if (analysis.vocabulary.transitionsUsed.length < 2) {
            suggestions.push({
                icon: 'fa-link',
                text: 'Thêm các từ nối (however, moreover, therefore...) để liên kết ý tốt hơn.'
            });
        }

        // Structure
        if (!analysis.structure.hasConclusion) {
            suggestions.push({
                icon: 'fa-flag-checkered',
                text: 'Thêm đoạn kết luận để tổng kết các ý chính.'
            });
        }

        // Word count
        if (analysis.basic.words < 100) {
            suggestions.push({
                icon: 'fa-expand',
                text: 'Bài viết còn ngắn. Hãy phát triển thêm các ý.'
            });
        }

        return suggestions;
    },

    /**
     * Calculate overall score
     */
    calculateScore(analysis) {
        let score = 0;
        
        // Readability (25%)
        score += (analysis.readability.fleschScore / 100) * 25;
        
        // Vocabulary diversity (25%)
        score += Math.min(1, analysis.vocabulary.diversity / 50) * 25;
        
        // Structure (25%)
        score += (analysis.structure.structureScore / 100) * 25;
        
        // Error penalty (25%)
        const errorPenalty = Math.min(25, analysis.errors.length * 5);
        score += 25 - errorPenalty;

        return Math.round(Math.max(0, Math.min(100, score)));
    },

    // ====================================
    // UI UPDATES
    // ====================================
    
    /**
     * Update live stats
     */
    updateLiveStats() {
        const text = this.state.text;
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);

        this.elements.liveStats.words.textContent = words.length;
        this.elements.liveStats.chars.textContent = text.length;
        this.elements.liveStats.sentences.textContent = sentences.length;
    },

    /**
     * Render analysis results
     */
    renderAnalysis(analysis) {
        this.elements.analysisPanel.style.display = 'block';

        // Overview
        this.elements.sections.overview.innerHTML = `
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-value">${analysis.basic.words}</div>
                    <div class="stat-box-label">Từ</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-value">${analysis.basic.sentences}</div>
                    <div class="stat-box-label">Câu</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-value">${analysis.basic.avgWordLength}</div>
                    <div class="stat-box-label">Độ dài từ TB</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-value">${analysis.basic.avgSentenceLength}</div>
                    <div class="stat-box-label">Từ/Câu TB</div>
                </div>
            </div>
        `;

        // Score
        const scoreClass = analysis.score >= 80 ? 'score-excellent' : 
                          analysis.score >= 60 ? 'score-good' : 
                          analysis.score >= 40 ? 'score-fair' : 'score-poor';
        
        this.elements.sections.score.innerHTML = `
            <div class="score-circle ${scoreClass}">${analysis.score}</div>
            <p style="text-align: center; margin: 0; color: #6c757d;">
                ${this.getScoreDescription(analysis.score)}
            </p>
        `;

        // Readability
        this.elements.sections.readability.innerHTML = `
            <div style="margin-bottom: 12px;">
                <strong>${analysis.readability.level}</strong>
                <span style="color: #6c757d;"> - ${analysis.readability.description}</span>
            </div>
            <div class="readability-bar">
                <div class="readability-fill" style="width: ${analysis.readability.fleschScore}%"></div>
            </div>
            <div class="readability-labels">
                <span>Khó đọc</span>
                <span>Dễ đọc</span>
            </div>
        `;

        // Vocabulary
        this.elements.sections.vocabulary.innerHTML = `
            <p style="margin: 0 0 8px;">
                <strong>${analysis.vocabulary.diversity}%</strong> độ đa dạng từ vựng
                <br>
                <small>${analysis.vocabulary.uniqueWords} từ khác nhau / ${analysis.vocabulary.totalWords} tổng từ</small>
            </p>
            ${analysis.vocabulary.advancedWords.length > 0 ? `
                <div class="vocab-level">
                    ${analysis.vocabulary.advancedWords.map(w => `<span class="vocab-pill b1-b2">${w}</span>`).join('')}
                </div>
            ` : ''}
        `;

        // Errors
        if (analysis.errors.length > 0) {
            this.elements.sections.errors.innerHTML = analysis.errors.map(err => `
                <div class="error-item">
                    <div class="error-item-type">${err.type}</div>
                    <div class="error-item-text">"${err.text}"</div>
                    <div class="error-item-suggestion">→ ${err.suggestion}</div>
                </div>
            `).join('');
        } else {
            this.elements.sections.errors.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-check-circle" style="color: #27AE60; font-size: 2rem;"></i>
                    <p>Không phát hiện lỗi phổ biến</p>
                </div>
            `;
        }

        // Suggestions
        if (analysis.suggestions.length > 0) {
            this.elements.sections.suggestions.innerHTML = analysis.suggestions.map(sug => `
                <div class="suggestion-item">
                    <i class="fas ${sug.icon} suggestion-icon"></i>
                    ${sug.text}
                </div>
            `).join('');
        } else {
            this.elements.sections.suggestions.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-thumbs-up" style="color: #27AE60; font-size: 2rem;"></i>
                    <p>Bài viết đã tốt!</p>
                </div>
            `;
        }
    },

    /**
     * Show not enough text message
     */
    showNotEnoughText() {
        this.elements.analysisPanel.style.display = 'block';
        const content = `
            <div class="no-results">
                <i class="fas fa-edit" style="color: #F47C26; font-size: 2rem;"></i>
                <p>Vui lòng viết ít nhất ${this.config.minWordsForAnalysis} từ để phân tích.</p>
            </div>
        `;
        
        Object.values(this.elements.sections).forEach(section => {
            section.innerHTML = content;
        });
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    getWordCount() {
        return this.state.text.trim().split(/\s+/).filter(w => w.length > 0).length;
    },

    getReadabilityLevel(score) {
        if (score >= 90) return 'Rất dễ đọc';
        if (score >= 70) return 'Dễ đọc';
        if (score >= 50) return 'Trung bình';
        if (score >= 30) return 'Hơi khó';
        return 'Khó đọc';
    },

    getReadabilityDescription(score) {
        if (score >= 90) return 'Phù hợp mọi đối tượng';
        if (score >= 70) return 'Phù hợp học sinh cấp 2';
        if (score >= 50) return 'Phù hợp học sinh cấp 3';
        if (score >= 30) return 'Phù hợp sinh viên';
        return 'Cần kiến thức chuyên sâu';
    },

    getScoreDescription(score) {
        if (score >= 80) return 'Xuất sắc! Bài viết rất tốt.';
        if (score >= 60) return 'Khá tốt! Tiếp tục phát huy.';
        if (score >= 40) return 'Trung bình. Cần cải thiện thêm.';
        return 'Cần luyện tập thêm nhiều.';
    },

    clear() {
        this.state.text = '';
        this.elements.textarea.value = '';
        this.elements.analysisPanel.style.display = 'none';
        this.updateLiveStats();
    },

    setText(text) {
        this.state.text = text;
        this.elements.textarea.value = text;
        this.updateLiveStats();
    },

    getText() {
        return this.state.text;
    },

    startAutoSave() {
        this.state.autoSaveTimer = setInterval(() => {
            if (this.state.text && this.callbacks.onAutoSave) {
                this.callbacks.onAutoSave(this.state.text);
            }
        }, this.config.autoSaveInterval);
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
            console.log('[WritingAnalyzer]', ...args);
        }
    }
};

// Export
window.WritingAnalyzer = WritingAnalyzer;

console.log('[Writing Analyzer] Module loaded');
