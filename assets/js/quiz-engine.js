/* ====================================
   QUIZ ENGINE - Assessment System
   Phase 3: Advanced Features
   Version: 1.0.0
   ==================================== */

/**
 * QuizEngine - Complete quiz and assessment system
 * Features:
 * - Multiple question types
 * - Timer and scoring
 * - Progress tracking
 * - Result analysis
 * - Review mode
 */
const QuizEngine = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        shuffleQuestions: true,
        shuffleOptions: true,
        showFeedback: true,
        showCorrectAnswer: true,
        allowSkip: true,
        allowReview: true,
        autoAdvance: false,
        autoAdvanceDelay: 1500,
        timeLimit: 0,               // 0 = no limit, in seconds
        passingScore: 60,
        debug: true
    },

    // Question Types
    questionTypes: {
        MULTIPLE_CHOICE: 'multiple-choice',
        TRUE_FALSE: 'true-false',
        FILL_BLANK: 'fill-blank',
        MATCHING: 'matching',
        ORDERING: 'ordering',
        SHORT_ANSWER: 'short-answer',
        LISTENING: 'listening',
        READING: 'reading'
    },

    // State
    state: {
        quiz: null,
        questions: [],
        currentIndex: 0,
        answers: {},
        score: 0,
        startTime: null,
        endTime: null,
        timeRemaining: 0,
        timerInterval: null,
        isComplete: false,
        isReview: false
    },

    // DOM Elements
    elements: {
        container: null,
        progress: null,
        question: null,
        options: null,
        navigation: null,
        timer: null
    },

    // Callbacks
    callbacks: {
        onStart: null,
        onAnswer: null,
        onComplete: null,
        onTimeUp: null
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize quiz engine
     */
    init(container, options = {}) {
        this.config = { ...this.config, ...options };

        if (typeof container === 'string') {
            this.elements.container = document.querySelector(container);
        } else {
            this.elements.container = container;
        }

        if (!this.elements.container) {
            console.error('[QuizEngine] Container not found');
            return null;
        }

        this.log('Quiz Engine initialized');
        return this;
    },

    /**
     * Load quiz data
     */
    loadQuiz(quizData) {
        // quizData format: { id, title, description, questions, timeLimit, settings }
        this.state.quiz = quizData;
        this.state.questions = [...quizData.questions];
        
        // Apply quiz settings
        if (quizData.settings) {
            this.config = { ...this.config, ...quizData.settings };
        }
        
        if (quizData.timeLimit) {
            this.config.timeLimit = quizData.timeLimit;
        }

        // Shuffle if enabled
        if (this.config.shuffleQuestions) {
            this.shuffleArray(this.state.questions);
        }

        this.resetState();
        this.log('Quiz loaded:', quizData.title);
        
        return this;
    },

    /**
     * Reset state
     */
    resetState() {
        this.state.currentIndex = 0;
        this.state.answers = {};
        this.state.score = 0;
        this.state.startTime = null;
        this.state.endTime = null;
        this.state.timeRemaining = this.config.timeLimit;
        this.state.isComplete = false;
        this.state.isReview = false;
        
        if (this.state.timerInterval) {
            clearInterval(this.state.timerInterval);
        }
    },

    // ====================================
    // QUIZ LIFECYCLE
    // ====================================
    
    /**
     * Start the quiz
     */
    start() {
        this.state.startTime = Date.now();
        this.renderUI();
        
        // Start timer if needed
        if (this.config.timeLimit > 0) {
            this.startTimer();
        }

        if (this.callbacks.onStart) {
            this.callbacks.onStart(this.state.quiz);
        }

        this.log('Quiz started');
    },

    /**
     * Complete the quiz
     */
    complete() {
        this.state.endTime = Date.now();
        this.state.isComplete = true;
        
        // Stop timer
        if (this.state.timerInterval) {
            clearInterval(this.state.timerInterval);
        }

        // Calculate final score
        this.calculateScore();

        // Show results
        this.renderResults();

        // Callback
        if (this.callbacks.onComplete) {
            this.callbacks.onComplete(this.getResults());
        }

        // Log to progress tracker
        if (typeof ProgressTracker !== 'undefined') {
            const timeSpent = (this.state.endTime - this.state.startTime) / 60000;
            ProgressTracker.logExercise('reading', this.state.score, timeSpent);
        }

        this.log('Quiz completed. Score:', this.state.score);
    },

    // ====================================
    // TIMER
    // ====================================
    
    /**
     * Start countdown timer
     */
    startTimer() {
        this.state.timeRemaining = this.config.timeLimit;
        this.updateTimerDisplay();

        this.state.timerInterval = setInterval(() => {
            this.state.timeRemaining--;
            this.updateTimerDisplay();

            if (this.state.timeRemaining <= 0) {
                this.onTimeUp();
            }
        }, 1000);
    },

    /**
     * Update timer display
     */
    updateTimerDisplay() {
        if (!this.elements.timer) return;

        const minutes = Math.floor(this.state.timeRemaining / 60);
        const seconds = this.state.timeRemaining % 60;
        const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        this.elements.timer.textContent = display;
        
        // Warning at 1 minute
        if (this.state.timeRemaining <= 60) {
            this.elements.timer.classList.add('warning');
        }
        if (this.state.timeRemaining <= 10) {
            this.elements.timer.classList.add('danger');
        }
    },

    /**
     * Handle time up
     */
    onTimeUp() {
        clearInterval(this.state.timerInterval);
        
        if (this.callbacks.onTimeUp) {
            this.callbacks.onTimeUp();
        }

        // Auto-complete quiz
        this.complete();
    },

    // ====================================
    // UI RENDERING
    // ====================================
    
    /**
     * Render main UI
     */
    renderUI() {
        const quiz = this.state.quiz;
        const hasTimer = this.config.timeLimit > 0;

        const html = `
            <div class="quiz-container">
                <!-- Header -->
                <div class="quiz-header">
                    <div class="quiz-info">
                        <h3 class="quiz-title">${quiz.title}</h3>
                        <p class="quiz-description">${quiz.description || ''}</p>
                    </div>
                    ${hasTimer ? `
                        <div class="quiz-timer">
                            <i class="fas fa-clock"></i>
                            <span class="timer-display">00:00</span>
                        </div>
                    ` : ''}
                </div>

                <!-- Progress -->
                <div class="quiz-progress">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div class="progress-text">
                        <span class="current-question">1</span>/<span class="total-questions">${this.state.questions.length}</span>
                    </div>
                </div>

                <!-- Question Area -->
                <div class="quiz-question-area"></div>

                <!-- Navigation -->
                <div class="quiz-navigation">
                    <button class="quiz-nav-btn prev" disabled>
                        <i class="fas fa-arrow-left"></i> Câu trước
                    </button>
                    ${this.config.allowSkip ? `
                        <button class="quiz-nav-btn skip">
                            Bỏ qua <i class="fas fa-forward"></i>
                        </button>
                    ` : ''}
                    <button class="quiz-nav-btn next">
                        Câu tiếp <i class="fas fa-arrow-right"></i>
                    </button>
                </div>

                <!-- Question Navigator -->
                <div class="quiz-question-nav">
                    ${this.state.questions.map((_, i) => `
                        <button class="qnav-btn ${i === 0 ? 'current' : ''}" data-index="${i}">${i + 1}</button>
                    `).join('')}
                </div>
            </div>
        `;

        this.elements.container.innerHTML = html;
        this.cacheElements();
        this.bindEvents();
        this.injectStyles();
        
        // Render first question
        this.renderQuestion(0);
    },

    /**
     * Cache DOM elements
     */
    cacheElements() {
        const c = this.elements.container;
        this.elements.progress = c.querySelector('.progress-fill');
        this.elements.currentQ = c.querySelector('.current-question');
        this.elements.questionArea = c.querySelector('.quiz-question-area');
        this.elements.timer = c.querySelector('.timer-display');
        this.elements.prevBtn = c.querySelector('.quiz-nav-btn.prev');
        this.elements.nextBtn = c.querySelector('.quiz-nav-btn.next');
        this.elements.skipBtn = c.querySelector('.quiz-nav-btn.skip');
        this.elements.qnavBtns = c.querySelectorAll('.qnav-btn');
    },

    /**
     * Bind events
     */
    bindEvents() {
        // Navigation buttons
        this.elements.prevBtn.addEventListener('click', () => this.prevQuestion());
        this.elements.nextBtn.addEventListener('click', () => this.nextQuestion());
        
        if (this.elements.skipBtn) {
            this.elements.skipBtn.addEventListener('click', () => this.skipQuestion());
        }

        // Question navigator
        this.elements.qnavBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.index);
                this.goToQuestion(index);
            });
        });
    },

    /**
     * Render a question
     */
    renderQuestion(index) {
        const question = this.state.questions[index];
        if (!question) return;

        this.state.currentIndex = index;
        this.updateProgress();

        let html = '';
        switch (question.type) {
            case this.questionTypes.MULTIPLE_CHOICE:
                html = this.renderMultipleChoice(question);
                break;
            case this.questionTypes.TRUE_FALSE:
                html = this.renderTrueFalse(question);
                break;
            case this.questionTypes.FILL_BLANK:
                html = this.renderFillBlank(question);
                break;
            case this.questionTypes.MATCHING:
                html = this.renderMatching(question);
                break;
            case this.questionTypes.ORDERING:
                html = this.renderOrdering(question);
                break;
            case this.questionTypes.SHORT_ANSWER:
                html = this.renderShortAnswer(question);
                break;
            case this.questionTypes.LISTENING:
                html = this.renderListening(question);
                break;
            case this.questionTypes.READING:
                html = this.renderReading(question);
                break;
            default:
                html = this.renderMultipleChoice(question);
        }

        this.elements.questionArea.innerHTML = html;
        this.bindQuestionEvents(question);

        // Restore previous answer if exists
        this.restoreAnswer(question);
    },

    /**
     * Render Multiple Choice question
     */
    renderMultipleChoice(question) {
        let options = [...question.options];
        if (this.config.shuffleOptions) {
            options = this.shuffleArray([...options]);
        }

        return `
            <div class="question-card" data-type="multiple-choice">
                <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                <div class="question-text">${question.text}</div>
                ${question.image ? `<img src="${question.image}" class="question-image" alt="">` : ''}
                <div class="options-list">
                    ${options.map((opt, i) => `
                        <label class="option-item">
                            <input type="radio" name="answer" value="${opt.id || i}">
                            <span class="option-marker">${String.fromCharCode(65 + i)}</span>
                            <span class="option-text">${opt.text || opt}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
    },

    /**
     * Render True/False question
     */
    renderTrueFalse(question) {
        return `
            <div class="question-card" data-type="true-false">
                <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                <div class="question-text">${question.text}</div>
                <div class="options-list tf-options">
                    <label class="option-item">
                        <input type="radio" name="answer" value="true">
                        <span class="option-marker"><i class="fas fa-check"></i></span>
                        <span class="option-text">Đúng (True)</span>
                    </label>
                    <label class="option-item">
                        <input type="radio" name="answer" value="false">
                        <span class="option-marker"><i class="fas fa-times"></i></span>
                        <span class="option-text">Sai (False)</span>
                    </label>
                </div>
            </div>
        `;
    },

    /**
     * Render Fill in the Blank question
     */
    renderFillBlank(question) {
        // Replace blanks with input fields
        let text = question.text.replace(/_{3,}|\[blank\]/gi, 
            `<input type="text" class="blank-input" placeholder="Điền vào chỗ trống">`
        );

        return `
            <div class="question-card" data-type="fill-blank">
                <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                <div class="question-text fill-blank-text">${text}</div>
                ${question.wordBank ? `
                    <div class="word-bank">
                        <strong>Ngân hàng từ:</strong>
                        ${question.wordBank.map(word => 
                            `<span class="word-chip">${word}</span>`
                        ).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Render Matching question
     */
    renderMatching(question) {
        let rightItems = [...question.pairs.map(p => p.right)];
        if (this.config.shuffleOptions) {
            rightItems = this.shuffleArray(rightItems);
        }

        return `
            <div class="question-card" data-type="matching">
                <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                <div class="question-text">${question.text}</div>
                <div class="matching-container">
                    <div class="matching-left">
                        ${question.pairs.map((pair, i) => `
                            <div class="match-item left" data-id="${i}">
                                <span class="match-number">${i + 1}</span>
                                <span class="match-text">${pair.left}</span>
                                <select class="match-select" data-left="${i}">
                                    <option value="">-- Chọn --</option>
                                    ${rightItems.map((r, j) => `
                                        <option value="${j}">${String.fromCharCode(65 + j)}</option>
                                    `).join('')}
                                </select>
                            </div>
                        `).join('')}
                    </div>
                    <div class="matching-right">
                        ${rightItems.map((item, i) => `
                            <div class="match-item right" data-id="${i}">
                                <span class="match-letter">${String.fromCharCode(65 + i)}</span>
                                <span class="match-text">${item}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Render Ordering question
     */
    renderOrdering(question) {
        let items = [...question.items];
        if (this.config.shuffleOptions) {
            items = this.shuffleArray(items);
        }

        return `
            <div class="question-card" data-type="ordering">
                <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                <div class="question-text">${question.text}</div>
                <div class="ordering-list" data-correct='${JSON.stringify(question.correctOrder)}'>
                    ${items.map((item, i) => `
                        <div class="order-item" draggable="true" data-id="${item.id || i}">
                            <span class="order-handle"><i class="fas fa-grip-vertical"></i></span>
                            <span class="order-text">${item.text || item}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    /**
     * Render Short Answer question
     */
    renderShortAnswer(question) {
        return `
            <div class="question-card" data-type="short-answer">
                <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                <div class="question-text">${question.text}</div>
                <textarea class="short-answer-input" placeholder="Nhập câu trả lời của bạn..." rows="4"></textarea>
            </div>
        `;
    },

    /**
     * Render Listening question
     */
    renderListening(question) {
        return `
            <div class="question-card" data-type="listening">
                <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                <div class="listening-player">
                    <audio class="listening-audio" src="${question.audio}" preload="auto"></audio>
                    <button class="play-audio-btn">
                        <i class="fas fa-play"></i> Nghe
                    </button>
                    <span class="play-count">Đã nghe: <strong>0</strong> lần</span>
                </div>
                <div class="question-text">${question.text}</div>
                ${this.renderMultipleChoiceOptions(question.options)}
            </div>
        `;
    },

    /**
     * Render Reading question
     */
    renderReading(question) {
        return `
            <div class="question-card" data-type="reading">
                <div class="reading-passage">
                    <h4><i class="fas fa-book-open"></i> Đoạn văn</h4>
                    <div class="passage-text">${question.passage}</div>
                </div>
                <div class="question-section">
                    <div class="question-number">Câu ${this.state.currentIndex + 1}</div>
                    <div class="question-text">${question.text}</div>
                    ${this.renderMultipleChoiceOptions(question.options)}
                </div>
            </div>
        `;
    },

    /**
     * Helper: Render multiple choice options
     */
    renderMultipleChoiceOptions(options) {
        return `
            <div class="options-list">
                ${options.map((opt, i) => `
                    <label class="option-item">
                        <input type="radio" name="answer" value="${opt.id || i}">
                        <span class="option-marker">${String.fromCharCode(65 + i)}</span>
                        <span class="option-text">${opt.text || opt}</span>
                    </label>
                `).join('')}
            </div>
        `;
    },

    /**
     * Bind question-specific events
     */
    bindQuestionEvents(question) {
        const questionArea = this.elements.questionArea;

        // Multiple choice & True/False
        const radioInputs = questionArea.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.saveAnswer(question, input.value);
                this.highlightSelectedOption(input);
                
                if (this.config.autoAdvance && !this.state.isReview) {
                    setTimeout(() => this.nextQuestion(), this.config.autoAdvanceDelay);
                }
            });
        });

        // Fill blank
        const blankInputs = questionArea.querySelectorAll('.blank-input');
        blankInputs.forEach((input, i) => {
            input.addEventListener('blur', () => {
                const answers = Array.from(questionArea.querySelectorAll('.blank-input'))
                    .map(inp => inp.value);
                this.saveAnswer(question, answers);
            });
        });

        // Matching
        const matchSelects = questionArea.querySelectorAll('.match-select');
        matchSelects.forEach(select => {
            select.addEventListener('change', () => {
                const matches = {};
                questionArea.querySelectorAll('.match-select').forEach(s => {
                    if (s.value) {
                        matches[s.dataset.left] = s.value;
                    }
                });
                this.saveAnswer(question, matches);
            });
        });

        // Ordering - Drag and Drop
        const orderItems = questionArea.querySelectorAll('.order-item');
        this.setupDragDrop(orderItems, question);

        // Short answer
        const shortAnswerInput = questionArea.querySelector('.short-answer-input');
        if (shortAnswerInput) {
            shortAnswerInput.addEventListener('blur', () => {
                this.saveAnswer(question, shortAnswerInput.value);
            });
        }

        // Listening audio
        const playBtn = questionArea.querySelector('.play-audio-btn');
        if (playBtn) {
            const audio = questionArea.querySelector('.listening-audio');
            const countEl = questionArea.querySelector('.play-count strong');
            let playCount = 0;

            playBtn.addEventListener('click', () => {
                audio.play();
                playCount++;
                countEl.textContent = playCount;
            });
        }

        // Word bank chips
        const wordChips = questionArea.querySelectorAll('.word-chip');
        wordChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const activeInput = document.activeElement;
                if (activeInput && activeInput.classList.contains('blank-input')) {
                    activeInput.value = chip.textContent;
                    chip.classList.add('used');
                }
            });
        });
    },

    /**
     * Setup drag and drop for ordering
     */
    setupDragDrop(items, question) {
        let draggedItem = null;

        items.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                draggedItem = item;
                item.classList.add('dragging');
            });

            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
                this.saveOrderAnswer(question);
            });

            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                const afterElement = this.getDragAfterElement(item.parentElement, e.clientY);
                if (afterElement == null) {
                    item.parentElement.appendChild(draggedItem);
                } else {
                    item.parentElement.insertBefore(draggedItem, afterElement);
                }
            });
        });
    },

    /**
     * Get element to insert after during drag
     */
    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.order-item:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    },

    /**
     * Save ordering answer
     */
    saveOrderAnswer(question) {
        const items = this.elements.questionArea.querySelectorAll('.order-item');
        const order = Array.from(items).map(item => item.dataset.id);
        this.saveAnswer(question, order);
    },

    // ====================================
    // ANSWER HANDLING
    // ====================================
    
    /**
     * Save answer
     */
    saveAnswer(question, answer) {
        this.state.answers[question.id] = {
            questionId: question.id,
            answer: answer,
            timestamp: Date.now()
        };

        // Update nav button
        this.updateNavButton(this.state.currentIndex, true);

        if (this.callbacks.onAnswer) {
            this.callbacks.onAnswer(question, answer);
        }
    },

    /**
     * Restore previous answer
     */
    restoreAnswer(question) {
        const saved = this.state.answers[question.id];
        if (!saved) return;

        const questionArea = this.elements.questionArea;
        const answer = saved.answer;

        switch (question.type) {
            case this.questionTypes.MULTIPLE_CHOICE:
            case this.questionTypes.TRUE_FALSE:
            case this.questionTypes.LISTENING:
            case this.questionTypes.READING:
                const radio = questionArea.querySelector(`input[value="${answer}"]`);
                if (radio) {
                    radio.checked = true;
                    this.highlightSelectedOption(radio);
                }
                break;

            case this.questionTypes.FILL_BLANK:
                if (Array.isArray(answer)) {
                    questionArea.querySelectorAll('.blank-input').forEach((input, i) => {
                        input.value = answer[i] || '';
                    });
                }
                break;

            case this.questionTypes.MATCHING:
                Object.entries(answer).forEach(([left, right]) => {
                    const select = questionArea.querySelector(`.match-select[data-left="${left}"]`);
                    if (select) select.value = right;
                });
                break;

            case this.questionTypes.SHORT_ANSWER:
                const textarea = questionArea.querySelector('.short-answer-input');
                if (textarea) textarea.value = answer;
                break;
        }
    },

    /**
     * Highlight selected option
     */
    highlightSelectedOption(input) {
        const options = this.elements.questionArea.querySelectorAll('.option-item');
        options.forEach(opt => opt.classList.remove('selected'));
        input.closest('.option-item').classList.add('selected');
    },

    // ====================================
    // NAVIGATION
    // ====================================
    
    prevQuestion() {
        if (this.state.currentIndex > 0) {
            this.renderQuestion(this.state.currentIndex - 1);
        }
    },

    nextQuestion() {
        if (this.state.currentIndex < this.state.questions.length - 1) {
            this.renderQuestion(this.state.currentIndex + 1);
        } else {
            // Last question - show confirm
            this.confirmSubmit();
        }
    },

    skipQuestion() {
        this.nextQuestion();
    },

    goToQuestion(index) {
        if (index >= 0 && index < this.state.questions.length) {
            this.renderQuestion(index);
        }
    },

    /**
     * Confirm submit quiz
     */
    confirmSubmit() {
        const unanswered = this.state.questions.filter(q => !this.state.answers[q.id]).length;
        
        let message = 'Bạn có chắc muốn nộp bài?';
        if (unanswered > 0) {
            message = `Còn ${unanswered} câu chưa trả lời. Bạn có chắc muốn nộp bài?`;
        }

        if (confirm(message)) {
            this.complete();
        }
    },

    /**
     * Update progress display
     */
    updateProgress() {
        const current = this.state.currentIndex + 1;
        const total = this.state.questions.length;
        const percent = (current / total) * 100;

        this.elements.progress.style.width = percent + '%';
        this.elements.currentQ.textContent = current;

        // Update nav buttons
        this.elements.prevBtn.disabled = this.state.currentIndex === 0;
        
        if (this.state.currentIndex === total - 1) {
            this.elements.nextBtn.innerHTML = 'Nộp bài <i class="fas fa-check"></i>';
        } else {
            this.elements.nextBtn.innerHTML = 'Câu tiếp <i class="fas fa-arrow-right"></i>';
        }

        // Update question nav
        this.elements.qnavBtns.forEach((btn, i) => {
            btn.classList.remove('current');
            if (i === this.state.currentIndex) {
                btn.classList.add('current');
            }
        });
    },

    /**
     * Update nav button status
     */
    updateNavButton(index, answered) {
        const btn = this.elements.qnavBtns[index];
        if (btn && answered) {
            btn.classList.add('answered');
        }
    },

    // ====================================
    // SCORING & RESULTS
    // ====================================
    
    /**
     * Calculate score
     */
    calculateScore() {
        let correct = 0;
        const results = [];

        this.state.questions.forEach(question => {
            const userAnswer = this.state.answers[question.id];
            const isCorrect = this.checkAnswer(question, userAnswer?.answer);
            
            if (isCorrect) correct++;

            results.push({
                question: question,
                userAnswer: userAnswer?.answer,
                isCorrect: isCorrect,
                correctAnswer: question.answer || question.correctAnswer
            });
        });

        this.state.score = Math.round((correct / this.state.questions.length) * 100);
        this.state.results = results;
        this.state.correctCount = correct;
    },

    /**
     * Check if answer is correct
     */
    checkAnswer(question, userAnswer) {
        if (!userAnswer) return false;

        const correct = question.answer || question.correctAnswer;

        switch (question.type) {
            case this.questionTypes.MULTIPLE_CHOICE:
            case this.questionTypes.TRUE_FALSE:
            case this.questionTypes.LISTENING:
            case this.questionTypes.READING:
                return String(userAnswer) === String(correct);

            case this.questionTypes.FILL_BLANK:
                if (Array.isArray(userAnswer) && Array.isArray(correct)) {
                    return userAnswer.every((ans, i) => 
                        ans.toLowerCase().trim() === correct[i].toLowerCase().trim()
                    );
                }
                return userAnswer.toLowerCase().trim() === correct.toLowerCase().trim();

            case this.questionTypes.MATCHING:
                return JSON.stringify(userAnswer) === JSON.stringify(correct);

            case this.questionTypes.ORDERING:
                return JSON.stringify(userAnswer) === JSON.stringify(correct);

            case this.questionTypes.SHORT_ANSWER:
                // Allow multiple correct answers
                if (Array.isArray(correct)) {
                    return correct.some(c => 
                        userAnswer.toLowerCase().trim().includes(c.toLowerCase().trim())
                    );
                }
                return userAnswer.toLowerCase().trim() === correct.toLowerCase().trim();

            default:
                return false;
        }
    },

    /**
     * Get results object
     */
    getResults() {
        const timeSpent = this.state.endTime - this.state.startTime;

        return {
            quizId: this.state.quiz.id,
            quizTitle: this.state.quiz.title,
            score: this.state.score,
            correctCount: this.state.correctCount,
            totalQuestions: this.state.questions.length,
            passed: this.state.score >= this.config.passingScore,
            timeSpent: timeSpent,
            timeSpentFormatted: this.formatTime(Math.round(timeSpent / 1000)),
            answers: this.state.answers,
            results: this.state.results
        };
    },

    // ====================================
    // RESULTS UI
    // ====================================
    
    /**
     * Render results
     */
    renderResults() {
        const results = this.getResults();
        const passed = results.passed;

        const html = `
            <div class="quiz-results">
                <div class="results-header ${passed ? 'passed' : 'failed'}">
                    <div class="results-icon">
                        <i class="fas ${passed ? 'fa-trophy' : 'fa-redo'}"></i>
                    </div>
                    <h2>${passed ? 'Chúc mừng!' : 'Chưa đạt!'}</h2>
                    <p>${passed ? 'Bạn đã hoàn thành bài kiểm tra xuất sắc!' : 'Hãy ôn tập và thử lại nhé!'}</p>
                </div>

                <div class="results-score">
                    <div class="score-circle ${this.getScoreClass(results.score)}">
                        <span class="score-value">${results.score}%</span>
                        <span class="score-label">Điểm số</span>
                    </div>
                </div>

                <div class="results-stats">
                    <div class="stat-item">
                        <i class="fas fa-check-circle text-success"></i>
                        <div class="stat-value">${results.correctCount}</div>
                        <div class="stat-label">Câu đúng</div>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-times-circle text-danger"></i>
                        <div class="stat-value">${results.totalQuestions - results.correctCount}</div>
                        <div class="stat-label">Câu sai</div>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-clock text-primary"></i>
                        <div class="stat-value">${results.timeSpentFormatted}</div>
                        <div class="stat-label">Thời gian</div>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-percentage text-warning"></i>
                        <div class="stat-value">${this.config.passingScore}%</div>
                        <div class="stat-label">Điểm đạt</div>
                    </div>
                </div>

                <div class="results-actions">
                    ${this.config.allowReview ? `
                        <button class="results-btn review">
                            <i class="fas fa-search"></i> Xem lại đáp án
                        </button>
                    ` : ''}
                    <button class="results-btn retry">
                        <i class="fas fa-redo"></i> Làm lại
                    </button>
                </div>
            </div>
        `;

        this.elements.container.innerHTML = html;
        this.bindResultEvents();
    },

    /**
     * Bind result events
     */
    bindResultEvents() {
        const reviewBtn = this.elements.container.querySelector('.results-btn.review');
        const retryBtn = this.elements.container.querySelector('.results-btn.retry');

        if (reviewBtn) {
            reviewBtn.addEventListener('click', () => this.startReview());
        }

        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.retry());
        }
    },

    /**
     * Start review mode
     */
    startReview() {
        this.state.isReview = true;
        this.renderUI();
        
        // Add review styling and info
        this.elements.container.classList.add('review-mode');
    },

    /**
     * Retry quiz
     */
    retry() {
        this.resetState();
        
        if (this.config.shuffleQuestions) {
            this.shuffleArray(this.state.questions);
        }
        
        this.start();
    },

    // ====================================
    // STYLES
    // ====================================
    
    injectStyles() {
        if (document.getElementById('quizEngineStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'quizEngineStyles';
        styles.textContent = `
            .quiz-container {
                background: white;
                border-radius: 16px;
                padding: 32px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            }
            
            .quiz-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 24px;
            }
            
            .quiz-title {
                margin: 0 0 8px;
                font-family: 'Montserrat', sans-serif;
                color: #183B56;
            }
            
            .quiz-description {
                margin: 0;
                color: #6c757d;
            }
            
            .quiz-timer {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 12px 20px;
                background: #F9FAFC;
                border-radius: 8px;
                font-family: 'Montserrat', sans-serif;
                font-size: 1.25rem;
                font-weight: 700;
            }
            
            .quiz-timer.warning .timer-display { color: #F47C26; }
            .quiz-timer.danger .timer-display { color: #E74C3C; }
            
            .quiz-progress {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 24px;
            }
            
            .progress-bar {
                flex: 1;
                height: 8px;
                background: #E0E6ED;
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #F47C26, #FFA726);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .progress-text {
                font-weight: 600;
                color: #183B56;
            }
            
            .question-card {
                background: #F9FAFC;
                border-radius: 12px;
                padding: 24px;
                min-height: 300px;
            }
            
            .question-number {
                font-size: 0.85rem;
                color: #F47C26;
                font-weight: 600;
                margin-bottom: 12px;
            }
            
            .question-text {
                font-size: 1.1rem;
                color: #183B56;
                margin-bottom: 20px;
                line-height: 1.6;
            }
            
            .question-image {
                max-width: 100%;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            
            .options-list {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .option-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px;
                background: white;
                border: 2px solid #E0E6ED;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .option-item:hover {
                border-color: #F47C26;
            }
            
            .option-item.selected {
                border-color: #F47C26;
                background: #FFF3E0;
            }
            
            .option-item input {
                display: none;
            }
            
            .option-marker {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: #E0E6ED;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                color: #183B56;
                flex-shrink: 0;
            }
            
            .option-item.selected .option-marker {
                background: #F47C26;
                color: white;
            }
            
            .option-text {
                flex: 1;
            }
            
            /* Fill blank */
            .blank-input {
                padding: 8px 16px;
                border: 2px dashed #F47C26;
                border-radius: 4px;
                background: white;
                min-width: 120px;
                text-align: center;
                font-size: inherit;
            }
            
            .word-bank {
                margin-top: 20px;
                padding: 16px;
                background: white;
                border-radius: 8px;
            }
            
            .word-chip {
                display: inline-block;
                padding: 6px 14px;
                margin: 4px;
                background: #E3F2FD;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .word-chip:hover { background: #BBDEFB; }
            .word-chip.used { opacity: 0.5; text-decoration: line-through; }
            
            /* Matching */
            .matching-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
            }
            
            .match-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                background: white;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            
            .match-number, .match-letter {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.9rem;
            }
            
            .match-number { background: #F47C26; color: white; }
            .match-letter { background: #3498DB; color: white; }
            
            .match-select {
                padding: 8px;
                border: 1px solid #E0E6ED;
                border-radius: 4px;
                margin-left: auto;
            }
            
            /* Ordering */
            .order-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px;
                background: white;
                border: 2px solid #E0E6ED;
                border-radius: 8px;
                margin-bottom: 8px;
                cursor: grab;
                transition: all 0.2s;
            }
            
            .order-item:active { cursor: grabbing; }
            .order-item.dragging { opacity: 0.5; }
            
            .order-handle {
                color: #adb5bd;
            }
            
            /* Listening */
            .listening-player {
                display: flex;
                align-items: center;
                gap: 16px;
                padding: 16px;
                background: white;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            
            .play-audio-btn {
                padding: 12px 24px;
                background: #F47C26;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
            }
            
            .play-count {
                color: #6c757d;
            }
            
            /* Reading */
            .reading-passage {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                max-height: 250px;
                overflow-y: auto;
            }
            
            .reading-passage h4 {
                margin: 0 0 12px;
                color: #183B56;
            }
            
            .passage-text {
                line-height: 1.8;
                color: #333;
            }
            
            /* Navigation */
            .quiz-navigation {
                display: flex;
                justify-content: space-between;
                margin-top: 24px;
                gap: 12px;
            }
            
            .quiz-nav-btn {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .quiz-nav-btn.prev {
                background: #E0E6ED;
                color: #183B56;
            }
            
            .quiz-nav-btn.next {
                background: #F47C26;
                color: white;
            }
            
            .quiz-nav-btn.skip {
                background: transparent;
                color: #6c757d;
            }
            
            .quiz-nav-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .quiz-question-nav {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #E0E6ED;
            }
            
            .qnav-btn {
                width: 40px;
                height: 40px;
                border: 2px solid #E0E6ED;
                border-radius: 8px;
                background: white;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .qnav-btn.current {
                border-color: #F47C26;
                background: #FFF3E0;
            }
            
            .qnav-btn.answered {
                background: #27AE60;
                border-color: #27AE60;
                color: white;
            }
            
            /* Results */
            .quiz-results {
                text-align: center;
                padding: 40px;
            }
            
            .results-header {
                margin-bottom: 32px;
            }
            
            .results-icon {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                font-size: 2rem;
            }
            
            .results-header.passed .results-icon {
                background: #E8F5E9;
                color: #27AE60;
            }
            
            .results-header.failed .results-icon {
                background: #FFEBEE;
                color: #E74C3C;
            }
            
            .results-header h2 {
                margin: 0 0 8px;
                font-family: 'Montserrat', sans-serif;
                font-size: 2rem;
            }
            
            .score-circle {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 0 auto 32px;
                color: white;
            }
            
            .score-circle.excellent { background: linear-gradient(135deg, #27AE60, #2ECC71); }
            .score-circle.good { background: linear-gradient(135deg, #3498DB, #5DADE2); }
            .score-circle.fair { background: linear-gradient(135deg, #F47C26, #F39C12); }
            .score-circle.poor { background: linear-gradient(135deg, #E74C3C, #EC7063); }
            
            .score-value {
                font-family: 'Montserrat', sans-serif;
                font-size: 2.5rem;
                font-weight: 800;
            }
            
            .score-label {
                font-size: 0.9rem;
                opacity: 0.9;
            }
            
            .results-stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 32px;
            }
            
            .stat-item {
                padding: 20px;
                background: #F9FAFC;
                border-radius: 12px;
            }
            
            .stat-item i {
                font-size: 1.5rem;
                margin-bottom: 8px;
            }
            
            .stat-item .stat-value {
                font-family: 'Montserrat', sans-serif;
                font-size: 1.5rem;
                font-weight: 700;
                color: #183B56;
            }
            
            .stat-item .stat-label {
                font-size: 0.85rem;
                color: #6c757d;
            }
            
            .results-actions {
                display: flex;
                gap: 16px;
                justify-content: center;
            }
            
            .results-btn {
                padding: 14px 32px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .results-btn.review {
                background: #E0E6ED;
                color: #183B56;
            }
            
            .results-btn.retry {
                background: #F47C26;
                color: white;
            }
            
            /* Text colors */
            .text-success { color: #27AE60; }
            .text-danger { color: #E74C3C; }
            .text-primary { color: #3498DB; }
            .text-warning { color: #F47C26; }
            
            /* Mobile */
            @media (max-width: 576px) {
                .quiz-container {
                    padding: 20px;
                }
                
                .quiz-header {
                    flex-direction: column;
                    gap: 16px;
                }
                
                .matching-container {
                    grid-template-columns: 1fr;
                }
                
                .results-stats {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .quiz-navigation {
                    flex-wrap: wrap;
                }
            }
        `;

        document.head.appendChild(styles);
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    },

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
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
            console.log('[QuizEngine]', ...args);
        }
    }
};

// Export
window.QuizEngine = QuizEngine;

console.log('[Quiz Engine] Module loaded');
