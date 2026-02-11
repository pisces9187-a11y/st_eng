/* ====================================
   GRAMMAR CHECKER - English Grammar Analysis
   Phase 3: Advanced Features
   Version: 1.0.0
   ==================================== */

/**
 * GrammarChecker - English grammar analysis and correction
 * Features:
 * - Grammar rule checking
 * - Spelling suggestions
 * - Style recommendations
 * - Real-time error highlighting
 * - Learning mode with explanations
 */
const GrammarChecker = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        enableRealTime: true,
        checkDelay: 800,
        showExplanations: true,
        highlightErrors: true,
        maxSuggestions: 5,
        targetLevel: 'B1',
        debug: true
    },

    // Grammar Rules Database
    rules: {
        // Subject-Verb Agreement
        subjectVerb: [
            {
                pattern: /\b(he|she|it)\s+(have)\b/gi,
                correction: '$1 has',
                category: 'subject-verb-agreement',
                explanation: 'Với chủ ngữ ngôi thứ 3 số ít (he/she/it), động từ "have" phải chuyển thành "has".',
                level: 'A1'
            },
            {
                pattern: /\b(he|she|it)\s+(do)\s+not\b/gi,
                correction: '$1 does not',
                category: 'subject-verb-agreement',
                explanation: 'Với chủ ngữ ngôi thứ 3 số ít, dùng "does not" thay vì "do not".',
                level: 'A1'
            },
            {
                pattern: /\b(he|she|it)\s+(go|come|make|take|give|see|know|think|want|like|need)\b(?!\s+to)/gi,
                correction: (match, subject, verb) => `${subject} ${verb}s`,
                category: 'subject-verb-agreement',
                explanation: 'Động từ thường với chủ ngữ ngôi 3 số ít cần thêm -s/-es.',
                level: 'A1'
            },
            {
                pattern: /\beveryone\s+(are|were|have)\b/gi,
                correction: (match, verb) => {
                    const map = { 'are': 'is', 'were': 'was', 'have': 'has' };
                    return `everyone ${map[verb.toLowerCase()]}`;
                },
                category: 'subject-verb-agreement',
                explanation: '"Everyone" là đại từ số ít, dùng với động từ số ít.',
                level: 'A2'
            },
            {
                pattern: /\bnobody\s+(are|were|have)\b/gi,
                correction: (match, verb) => {
                    const map = { 'are': 'is', 'were': 'was', 'have': 'has' };
                    return `nobody ${map[verb.toLowerCase()]}`;
                },
                category: 'subject-verb-agreement',
                explanation: '"Nobody" là đại từ số ít, dùng với động từ số ít.',
                level: 'A2'
            }
        ],

        // Tense Errors
        tense: [
            {
                pattern: /\byesterday\s+I\s+(go|come|see|eat|make|do|have|get|take)\b/gi,
                correction: (match, verb) => {
                    const pastForms = {
                        'go': 'went', 'come': 'came', 'see': 'saw', 'eat': 'ate',
                        'make': 'made', 'do': 'did', 'have': 'had', 'get': 'got', 'take': 'took'
                    };
                    return `yesterday I ${pastForms[verb.toLowerCase()]}`;
                },
                category: 'tense',
                explanation: 'Với "yesterday", dùng thì quá khứ đơn (Past Simple).',
                level: 'A2'
            },
            {
                pattern: /\blast\s+(week|month|year)\s+I\s+(go|come|see|eat|make|do|have|get|take)\b/gi,
                correction: (match, time, verb) => {
                    const pastForms = {
                        'go': 'went', 'come': 'came', 'see': 'saw', 'eat': 'ate',
                        'make': 'made', 'do': 'did', 'have': 'had', 'get': 'got', 'take': 'took'
                    };
                    return `last ${time} I ${pastForms[verb.toLowerCase()]}`;
                },
                category: 'tense',
                explanation: 'Với "last week/month/year", dùng thì quá khứ đơn.',
                level: 'A2'
            },
            {
                pattern: /\bI\s+am\s+go\b/gi,
                correction: 'I am going',
                category: 'tense',
                explanation: 'Thì hiện tại tiếp diễn: be + V-ing.',
                level: 'A1'
            },
            {
                pattern: /\bsince\s+\d{4}\s+I\s+(work|live|study)\b/gi,
                correction: (match, verb) => match.replace(verb, `have been ${verb}ing`),
                category: 'tense',
                explanation: '"Since + thời điểm" thường đi với thì hiện tại hoàn thành hoặc hoàn thành tiếp diễn.',
                level: 'B1'
            }
        ],

        // Article Errors
        articles: [
            {
                pattern: /\b(go to|went to|going to)\s+the\s+(school|church|prison|bed|hospital)\b/gi,
                correction: '$1 $2',
                category: 'articles',
                explanation: 'Không dùng "the" trước school, church, prison, bed, hospital khi nói về mục đích chính của nơi đó.',
                level: 'A2'
            },
            {
                pattern: /\b(a)\s+([aeiou])/gi,
                correction: 'an $2',
                category: 'articles',
                explanation: 'Dùng "an" trước từ bắt đầu bằng nguyên âm (a, e, i, o, u).',
                level: 'A1'
            },
            {
                pattern: /\b(an)\s+([^aeiou\s])/gi,
                correction: 'a $2',
                category: 'articles',
                explanation: 'Dùng "a" trước từ bắt đầu bằng phụ âm.',
                level: 'A1',
                exceptions: ['hour', 'honest', 'honor', 'heir']
            },
            {
                pattern: /\bplay\s+the\s+(football|basketball|tennis|golf|chess)\b/gi,
                correction: 'play $1',
                category: 'articles',
                explanation: 'Không dùng "the" trước tên môn thể thao sau "play".',
                level: 'A2'
            },
            {
                pattern: /\bplay\s+(piano|guitar|violin|drums)\b/gi,
                correction: 'play the $1',
                category: 'articles',
                explanation: 'Dùng "the" trước tên nhạc cụ sau "play".',
                level: 'A2'
            }
        ],

        // Preposition Errors
        prepositions: [
            {
                pattern: /\bdepends\s+of\b/gi,
                correction: 'depends on',
                category: 'prepositions',
                explanation: 'Cụm từ đúng là "depends on" (phụ thuộc vào).',
                level: 'A2'
            },
            {
                pattern: /\binterested\s+for\b/gi,
                correction: 'interested in',
                category: 'prepositions',
                explanation: 'Cụm từ đúng là "interested in" (quan tâm đến).',
                level: 'A2'
            },
            {
                pattern: /\bgood\s+in\b/gi,
                correction: 'good at',
                category: 'prepositions',
                explanation: 'Cụm từ đúng là "good at" (giỏi về).',
                level: 'A2'
            },
            {
                pattern: /\bdifferent\s+of\b/gi,
                correction: 'different from',
                category: 'prepositions',
                explanation: 'Cụm từ đúng là "different from" (khác với).',
                level: 'A2'
            },
            {
                pattern: /\barrive\s+to\b/gi,
                correction: 'arrive at/in',
                category: 'prepositions',
                explanation: '"Arrive at" dùng cho nơi nhỏ, "arrive in" cho thành phố/quốc gia.',
                level: 'A2'
            },
            {
                pattern: /\blisten\s+(?!to)/gi,
                correction: 'listen to',
                category: 'prepositions',
                explanation: '"Listen" luôn đi với giới từ "to".',
                level: 'A1'
            },
            {
                pattern: /\bmarried\s+with\b/gi,
                correction: 'married to',
                category: 'prepositions',
                explanation: 'Cụm từ đúng là "married to" (kết hôn với).',
                level: 'B1'
            },
            {
                pattern: /\bon\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+morning\b/gi,
                correction: '$1 morning',
                category: 'prepositions',
                explanation: 'Không dùng "on" khi đã có "morning/afternoon/evening" sau ngày.',
                level: 'A2'
            }
        ],

        // Word Form Errors
        wordForm: [
            {
                pattern: /\bmore\s+better\b/gi,
                correction: 'better',
                category: 'word-form',
                explanation: '"Better" đã là dạng so sánh hơn, không cần thêm "more".',
                level: 'A2'
            },
            {
                pattern: /\bmore\s+worse\b/gi,
                correction: 'worse',
                category: 'word-form',
                explanation: '"Worse" đã là dạng so sánh hơn, không cần thêm "more".',
                level: 'A2'
            },
            {
                pattern: /\bthe\s+most\s+best\b/gi,
                correction: 'the best',
                category: 'word-form',
                explanation: '"Best" đã là dạng so sánh nhất, không cần thêm "most".',
                level: 'A2'
            },
            {
                pattern: /\bi\s+am\s+agree\b/gi,
                correction: 'I agree',
                category: 'word-form',
                explanation: '"Agree" là động từ, không dùng "be + agree".',
                level: 'A2'
            },
            {
                pattern: /\b(give|tell|show|send|teach)\s+to\s+me\b/gi,
                correction: '$1 me',
                category: 'word-form',
                explanation: 'Với các động từ cho/nhận, tân ngữ gián tiếp đi trực tiếp sau động từ.',
                level: 'B1'
            }
        ],

        // Uncountable Nouns
        uncountable: [
            {
                pattern: /\b(many|few)\s+(information|advice|furniture|equipment|news|money|luggage)\b/gi,
                correction: (match, quantifier, noun) => {
                    const replacement = quantifier.toLowerCase() === 'many' ? 'much' : 'little';
                    return `${replacement} ${noun}`;
                },
                category: 'uncountable',
                explanation: 'Đây là danh từ không đếm được, dùng "much/little" thay vì "many/few".',
                level: 'A2'
            },
            {
                pattern: /\b(informations|advices|furnitures|equipments|newses|moneys|luggages)\b/gi,
                correction: (match) => match.slice(0, -1),
                category: 'uncountable',
                explanation: 'Danh từ không đếm được không có dạng số nhiều.',
                level: 'A2'
            },
            {
                pattern: /\ba\s+(information|advice|furniture|equipment|news|money|luggage)\b/gi,
                correction: '$1',
                category: 'uncountable',
                explanation: 'Không dùng "a/an" với danh từ không đếm được.',
                level: 'A2'
            }
        ],

        // Verb Patterns
        verbPatterns: [
            {
                pattern: /\b(enjoy|finish|mind|suggest|avoid|consider|practice)\s+to\s+\w+/gi,
                correction: (match) => match.replace(/to\s+(\w+)/, '$1ing'),
                category: 'verb-pattern',
                explanation: 'Động từ này đi với V-ing, không phải "to V".',
                level: 'B1'
            },
            {
                pattern: /\b(want|need|hope|expect|decide|plan|agree|refuse|promise)\s+(\w+)ing\b/gi,
                correction: (match, verb, action) => `${verb} to ${action}`,
                category: 'verb-pattern',
                explanation: 'Động từ này đi với "to V", không phải V-ing.',
                level: 'B1'
            },
            {
                pattern: /\blet\s+(\w+)\s+to\b/gi,
                correction: 'let $1',
                category: 'verb-pattern',
                explanation: '"Let" đi với động từ nguyên thể không "to".',
                level: 'A2'
            },
            {
                pattern: /\bmake\s+(\w+)\s+to\b/gi,
                correction: 'make $1',
                category: 'verb-pattern',
                explanation: '"Make" (bắt buộc) đi với động từ nguyên thể không "to".',
                level: 'B1'
            }
        ],

        // Conditional Errors
        conditionals: [
            {
                pattern: /\bif\s+I\s+(will|would)\s+have\b/gi,
                correction: 'if I have',
                category: 'conditionals',
                explanation: 'Trong mệnh đề IF, không dùng "will/would".',
                level: 'B1'
            },
            {
                pattern: /\bif\s+I\s+would\s+be\b/gi,
                correction: 'if I were',
                category: 'conditionals',
                explanation: 'Câu điều kiện loại 2: if + past simple. Với "be" dùng "were" cho tất cả các ngôi.',
                level: 'B1'
            },
            {
                pattern: /\bif\s+I\s+was\s+you\b/gi,
                correction: 'if I were you',
                category: 'conditionals',
                explanation: 'Trong câu điều kiện giả định, dùng "were" cho tất cả các ngôi.',
                level: 'B1'
            }
        ],

        // Common Mistakes
        common: [
            {
                pattern: /\bvery\s+much\s+\w+er\b/gi,
                correction: 'much [comparative]',
                category: 'common',
                explanation: 'Với tính từ so sánh hơn, dùng "much" không phải "very much".',
                level: 'B1'
            },
            {
                pattern: /\btoo\s+much\s+(happy|sad|big|small|fast|slow|good|bad)\b/gi,
                correction: 'too $1',
                category: 'common',
                explanation: '"Too" + tính từ đếm được. Dùng "too much" với danh từ không đếm được.',
                level: 'A2'
            },
            {
                pattern: /\bpeoples\b/gi,
                correction: 'people',
                category: 'common',
                explanation: '"People" đã là số nhiều của "person".',
                level: 'A1'
            },
            {
                pattern: /\bchildrens\b/gi,
                correction: 'children',
                category: 'common',
                explanation: '"Children" đã là số nhiều của "child".',
                level: 'A1'
            }
        ]
    },

    // State
    state: {
        text: '',
        errors: [],
        checking: false,
        checkTimer: null
    },

    // DOM Elements
    elements: {
        container: null,
        input: null,
        output: null,
        errorList: null
    },

    // Callbacks
    callbacks: {
        onCheck: null,
        onError: null
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize grammar checker
     */
    init(options = {}) {
        this.config = { ...this.config, ...options };
        this.log('Grammar Checker initialized');
        return this;
    },

    /**
     * Create UI
     */
    createUI(container, options = {}) {
        if (typeof container === 'string') {
            this.elements.container = document.querySelector(container);
        } else {
            this.elements.container = container;
        }

        if (!this.elements.container) {
            console.error('[GrammarChecker] Container not found');
            return null;
        }

        const html = `
            <div class="grammar-checker">
                <div class="gc-header">
                    <h3><i class="fas fa-spell-check"></i> Kiểm tra ngữ pháp</h3>
                    <div class="gc-actions">
                        <select class="gc-level-select">
                            <option value="A1">A1 - Cơ bản</option>
                            <option value="A2">A2 - Sơ cấp</option>
                            <option value="B1" selected>B1 - Trung cấp</option>
                            <option value="B2">B2 - Trung cao cấp</option>
                            <option value="C1">C1 - Cao cấp</option>
                        </select>
                        <button class="gc-btn gc-btn-check">
                            <i class="fas fa-search"></i> Kiểm tra
                        </button>
                    </div>
                </div>

                <div class="gc-main">
                    <div class="gc-input-section">
                        <textarea 
                            class="gc-textarea" 
                            placeholder="${options.placeholder || 'Nhập hoặc dán văn bản tiếng Anh để kiểm tra ngữ pháp...'}"
                        ></textarea>
                        <div class="gc-stats">
                            <span><i class="fas fa-font"></i> <span class="stat-words">0</span> từ</span>
                            <span><i class="fas fa-exclamation-circle"></i> <span class="stat-errors">0</span> lỗi</span>
                        </div>
                    </div>

                    <div class="gc-output-section">
                        <div class="gc-highlighted-text"></div>
                        <div class="gc-errors-panel">
                            <h4><i class="fas fa-list"></i> Chi tiết lỗi</h4>
                            <div class="gc-errors-list"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.elements.container.innerHTML = html;
        this.cacheElements();
        this.bindEvents();
        this.injectStyles();

        return this;
    },

    /**
     * Cache DOM elements
     */
    cacheElements() {
        const c = this.elements.container;
        this.elements.input = c.querySelector('.gc-textarea');
        this.elements.output = c.querySelector('.gc-highlighted-text');
        this.elements.errorList = c.querySelector('.gc-errors-list');
        this.elements.checkBtn = c.querySelector('.gc-btn-check');
        this.elements.levelSelect = c.querySelector('.gc-level-select');
        this.elements.statsWords = c.querySelector('.stat-words');
        this.elements.statsErrors = c.querySelector('.stat-errors');
    },

    /**
     * Bind events
     */
    bindEvents() {
        // Input
        this.elements.input.addEventListener('input', (e) => {
            this.state.text = e.target.value;
            this.updateWordCount();

            if (this.config.enableRealTime) {
                this.scheduleCheck();
            }
        });

        // Check button
        this.elements.checkBtn.addEventListener('click', () => {
            this.check(this.state.text);
        });

        // Level select
        this.elements.levelSelect.addEventListener('change', (e) => {
            this.config.targetLevel = e.target.value;
            if (this.state.text) {
                this.check(this.state.text);
            }
        });
    },

    /**
     * Inject styles
     */
    injectStyles() {
        if (document.getElementById('grammarCheckerStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'grammarCheckerStyles';
        styles.textContent = `
            .grammar-checker {
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            }
            
            .gc-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 24px;
                background: #183B56;
                color: white;
            }
            
            .gc-header h3 {
                margin: 0;
                font-family: 'Montserrat', sans-serif;
            }
            
            .gc-actions {
                display: flex;
                gap: 12px;
                align-items: center;
            }
            
            .gc-level-select {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-size: 0.9rem;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                cursor: pointer;
            }
            
            .gc-level-select option {
                color: #183B56;
            }
            
            .gc-btn {
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
            
            .gc-btn-check {
                background: #F47C26;
                color: white;
            }
            
            .gc-btn-check:hover {
                background: #D35400;
            }
            
            .gc-main {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
                padding: 24px;
            }
            
            .gc-textarea {
                width: 100%;
                min-height: 300px;
                padding: 16px;
                border: 2px solid #E0E6ED;
                border-radius: 12px;
                font-size: 1rem;
                line-height: 1.8;
                resize: vertical;
                font-family: 'Open Sans', sans-serif;
            }
            
            .gc-textarea:focus {
                outline: none;
                border-color: #F47C26;
            }
            
            .gc-stats {
                display: flex;
                gap: 20px;
                margin-top: 12px;
                color: #6c757d;
                font-size: 0.9rem;
            }
            
            .gc-stats span {
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .gc-highlighted-text {
                padding: 16px;
                background: #F9FAFC;
                border-radius: 12px;
                min-height: 150px;
                line-height: 2;
                font-size: 1rem;
                margin-bottom: 16px;
            }
            
            .gc-highlighted-text:empty::before {
                content: 'Kết quả kiểm tra sẽ hiển thị ở đây...';
                color: #adb5bd;
            }
            
            .gc-error-highlight {
                background: #FFEBEE;
                color: #E74C3C;
                border-bottom: 2px wavy #E74C3C;
                cursor: pointer;
                padding: 2px 4px;
                border-radius: 2px;
                transition: background 0.2s;
            }
            
            .gc-error-highlight:hover {
                background: #FFCDD2;
            }
            
            .gc-error-highlight.warning {
                background: #FFF3E0;
                color: #F47C26;
                border-bottom-color: #F47C26;
            }
            
            .gc-errors-panel h4 {
                margin: 0 0 16px 0;
                color: #183B56;
                font-family: 'Montserrat', sans-serif;
                font-size: 1rem;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .gc-errors-list {
                max-height: 300px;
                overflow-y: auto;
            }
            
            .gc-error-item {
                padding: 16px;
                background: white;
                border-radius: 8px;
                margin-bottom: 12px;
                border-left: 4px solid #E74C3C;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            }
            
            .gc-error-item.warning {
                border-left-color: #F47C26;
            }
            
            .gc-error-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            
            .gc-error-category {
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                padding: 4px 8px;
                border-radius: 4px;
                background: #FFEBEE;
                color: #E74C3C;
            }
            
            .gc-error-level {
                font-size: 0.75rem;
                padding: 2px 8px;
                border-radius: 10px;
                background: #E0E6ED;
                color: #666;
            }
            
            .gc-error-original {
                color: #E74C3C;
                text-decoration: line-through;
                margin-right: 8px;
            }
            
            .gc-error-correction {
                color: #27AE60;
                font-weight: 600;
            }
            
            .gc-error-explanation {
                margin-top: 8px;
                padding: 8px 12px;
                background: #F8F9FA;
                border-radius: 6px;
                font-size: 0.85rem;
                color: #555;
                line-height: 1.5;
            }
            
            .gc-error-actions {
                display: flex;
                gap: 8px;
                margin-top: 12px;
            }
            
            .gc-fix-btn {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 0.8rem;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .gc-fix-btn.apply {
                background: #27AE60;
                color: white;
            }
            
            .gc-fix-btn.apply:hover {
                background: #229954;
            }
            
            .gc-fix-btn.ignore {
                background: #E0E6ED;
                color: #666;
            }
            
            .gc-no-errors {
                text-align: center;
                padding: 40px 20px;
                color: #6c757d;
            }
            
            .gc-no-errors i {
                font-size: 3rem;
                color: #27AE60;
                margin-bottom: 16px;
                display: block;
            }
            
            /* Mobile */
            @media (max-width: 768px) {
                .gc-main {
                    grid-template-columns: 1fr;
                }
                
                .gc-header {
                    flex-direction: column;
                    gap: 16px;
                }
            }
        `;

        document.head.appendChild(styles);
    },

    // ====================================
    // CHECKING
    // ====================================
    
    /**
     * Schedule check with debounce
     */
    scheduleCheck() {
        if (this.state.checkTimer) {
            clearTimeout(this.state.checkTimer);
        }

        this.state.checkTimer = setTimeout(() => {
            this.check(this.state.text);
        }, this.config.checkDelay);
    },

    /**
     * Check text for grammar errors
     */
    check(text) {
        if (!text || text.trim().length < 3) {
            this.clearResults();
            return [];
        }

        this.state.checking = true;
        this.state.errors = [];

        // Check all rule categories
        Object.entries(this.rules).forEach(([category, rules]) => {
            rules.forEach(rule => {
                this.checkRule(text, rule, category);
            });
        });

        // Sort errors by position
        this.state.errors.sort((a, b) => a.position - b.position);

        // Render results
        this.renderResults(text);
        this.state.checking = false;

        // Update stats
        this.elements.statsErrors.textContent = this.state.errors.length;

        // Callback
        if (this.callbacks.onCheck) {
            this.callbacks.onCheck(this.state.errors);
        }

        this.log(`Found ${this.state.errors.length} errors`);
        return this.state.errors;
    },

    /**
     * Check a single rule
     */
    checkRule(text, rule, category) {
        const levelOrder = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
        const targetIndex = levelOrder.indexOf(this.config.targetLevel);
        const ruleIndex = levelOrder.indexOf(rule.level || 'B1');

        // Only check rules at or below target level
        if (ruleIndex > targetIndex) return;

        let match;
        const regex = new RegExp(rule.pattern.source, rule.pattern.flags);

        while ((match = regex.exec(text)) !== null) {
            // Check exceptions
            if (rule.exceptions) {
                const lowerMatch = match[0].toLowerCase();
                if (rule.exceptions.some(ex => lowerMatch.includes(ex))) {
                    continue;
                }
            }

            // Calculate correction
            let correction;
            if (typeof rule.correction === 'function') {
                correction = rule.correction(...match);
            } else {
                correction = match[0].replace(rule.pattern, rule.correction);
            }

            this.state.errors.push({
                id: `error-${Date.now()}-${match.index}`,
                original: match[0],
                correction: correction,
                position: match.index,
                length: match[0].length,
                category: rule.category || category,
                explanation: rule.explanation,
                level: rule.level || 'B1'
            });
        }
    },

    /**
     * Check text (direct API)
     */
    checkText(text) {
        return this.check(text);
    },

    // ====================================
    // RENDERING
    // ====================================
    
    /**
     * Render check results
     */
    renderResults(text) {
        // Render highlighted text
        this.renderHighlightedText(text);
        
        // Render error list
        this.renderErrorList();
    },

    /**
     * Render highlighted text
     */
    renderHighlightedText(text) {
        if (this.state.errors.length === 0) {
            this.elements.output.innerHTML = text;
            return;
        }

        let result = '';
        let lastIndex = 0;

        this.state.errors.forEach((error, idx) => {
            // Add text before error
            result += this.escapeHtml(text.substring(lastIndex, error.position));
            
            // Add highlighted error
            result += `<span class="gc-error-highlight" data-error-id="${error.id}" title="${error.correction}">${this.escapeHtml(error.original)}</span>`;
            
            lastIndex = error.position + error.length;
        });

        // Add remaining text
        result += this.escapeHtml(text.substring(lastIndex));

        this.elements.output.innerHTML = result;

        // Add click handlers
        this.elements.output.querySelectorAll('.gc-error-highlight').forEach(el => {
            el.addEventListener('click', () => {
                const errorId = el.dataset.errorId;
                this.scrollToError(errorId);
            });
        });
    },

    /**
     * Render error list
     */
    renderErrorList() {
        if (this.state.errors.length === 0) {
            this.elements.errorList.innerHTML = `
                <div class="gc-no-errors">
                    <i class="fas fa-check-circle"></i>
                    <p>Không tìm thấy lỗi ngữ pháp!</p>
                </div>
            `;
            return;
        }

        const html = this.state.errors.map((error, idx) => `
            <div class="gc-error-item" id="${error.id}">
                <div class="gc-error-header">
                    <span class="gc-error-category">${this.getCategoryLabel(error.category)}</span>
                    <span class="gc-error-level">${error.level}</span>
                </div>
                <div class="gc-error-text">
                    <span class="gc-error-original">${error.original}</span>
                    <i class="fas fa-arrow-right" style="color: #6c757d;"></i>
                    <span class="gc-error-correction">${error.correction}</span>
                </div>
                ${this.config.showExplanations ? `
                    <div class="gc-error-explanation">
                        <i class="fas fa-info-circle"></i> ${error.explanation}
                    </div>
                ` : ''}
                <div class="gc-error-actions">
                    <button class="gc-fix-btn apply" data-index="${idx}">
                        <i class="fas fa-check"></i> Sửa lỗi
                    </button>
                    <button class="gc-fix-btn ignore" data-index="${idx}">
                        <i class="fas fa-times"></i> Bỏ qua
                    </button>
                </div>
            </div>
        `).join('');

        this.elements.errorList.innerHTML = html;

        // Add button handlers
        this.elements.errorList.querySelectorAll('.gc-fix-btn.apply').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.index);
                this.applyFix(index);
            });
        });

        this.elements.errorList.querySelectorAll('.gc-fix-btn.ignore').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.index);
                this.ignoreError(index);
            });
        });
    },

    /**
     * Clear results
     */
    clearResults() {
        this.state.errors = [];
        this.elements.output.innerHTML = '';
        this.elements.errorList.innerHTML = '';
        this.elements.statsErrors.textContent = '0';
    },

    // ====================================
    // ACTIONS
    // ====================================
    
    /**
     * Apply a fix
     */
    applyFix(index) {
        const error = this.state.errors[index];
        if (!error) return;

        const text = this.state.text;
        const newText = text.substring(0, error.position) + 
                       error.correction + 
                       text.substring(error.position + error.length);

        this.state.text = newText;
        this.elements.input.value = newText;
        
        // Recheck
        this.check(newText);

        // Toast notification
        if (typeof UIComponents !== 'undefined') {
            UIComponents.toast.success('Đã sửa lỗi!');
        }
    },

    /**
     * Apply all fixes
     */
    applyAllFixes() {
        // Apply from last to first to preserve positions
        const sortedErrors = [...this.state.errors].sort((a, b) => b.position - a.position);
        let text = this.state.text;

        sortedErrors.forEach(error => {
            text = text.substring(0, error.position) + 
                   error.correction + 
                   text.substring(error.position + error.length);
        });

        this.state.text = text;
        this.elements.input.value = text;
        this.check(text);

        if (typeof UIComponents !== 'undefined') {
            UIComponents.toast.success(`Đã sửa ${sortedErrors.length} lỗi!`);
        }
    },

    /**
     * Ignore an error
     */
    ignoreError(index) {
        this.state.errors.splice(index, 1);
        this.renderResults(this.state.text);
        this.elements.statsErrors.textContent = this.state.errors.length;
    },

    /**
     * Scroll to error in list
     */
    scrollToError(errorId) {
        const errorEl = document.getElementById(errorId);
        if (errorEl) {
            errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            errorEl.style.animation = 'pulse 0.5s';
        }
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    getCategoryLabel(category) {
        const labels = {
            'subject-verb-agreement': 'Hòa hợp S-V',
            'tense': 'Thì',
            'articles': 'Mạo từ',
            'prepositions': 'Giới từ',
            'word-form': 'Dạng từ',
            'uncountable': 'Danh từ không đếm được',
            'verb-pattern': 'Cấu trúc động từ',
            'conditionals': 'Câu điều kiện',
            'common': 'Lỗi thường gặp'
        };
        return labels[category] || category;
    },

    updateWordCount() {
        const words = this.state.text.trim().split(/\s+/).filter(w => w.length > 0);
        this.elements.statsWords.textContent = words.length;
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    setText(text) {
        this.state.text = text;
        if (this.elements.input) {
            this.elements.input.value = text;
            this.updateWordCount();
        }
        return this;
    },

    getText() {
        return this.state.text;
    },

    getErrors() {
        return this.state.errors;
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
            console.log('[GrammarChecker]', ...args);
        }
    }
};

// Export
window.GrammarChecker = GrammarChecker;

console.log('[Grammar Checker] Module loaded');
